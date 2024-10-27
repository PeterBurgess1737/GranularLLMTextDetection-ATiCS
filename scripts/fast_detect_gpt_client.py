import argparse
import datetime
import pathlib
import socket
import struct
import traceback

import torch
from fast_detect_gpt import get_sampling_discrepancy_analytic
from local_infer import ProbEstimator
from model import load_tokenizer, load_model

LOG_FILE = pathlib.Path(__file__).parent / "fast_detect_gpt_client.log"


def log(text):
    with LOG_FILE.open("a", encoding="utf-8") as f:
        # formatted_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        formatted_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")[:-3]
        print(f"{formatted_time} - {text}", file=f)


class Evaluator:
    def __init__(self, args):
        # region - Adapted from `local_infer.py`
        # load model
        self.scoring_tokenizer = load_tokenizer(args.scoring_model_name, args.dataset, args.cache_dir)
        self.scoring_model = load_model(args.scoring_model_name, args.device, args.cache_dir)
        self.scoring_model.eval()

        self.reference_tokenizer = None
        self.reference_model = None
        if args.reference_model_name != args.scoring_model_name:
            self.reference_tokenizer = load_tokenizer(args.reference_model_name, args.dataset, args.cache_dir)
            self.reference_model = load_model(args.reference_model_name, args.device, args.cache_dir)
            self.reference_model.eval()

        # evaluate criterion
        self.criterion_fn = get_sampling_discrepancy_analytic
        self.prob_estimator = ProbEstimator(args)
        # endregion

        # Also save args for later use
        self.args = args

    def evaluate(self, text):
        """
        :param text: The input text to be evaluated by the scoring and reference models.
        :return: A tuple containing the evaluation criterion and the probability estimate.
        """

        # region - Adapted from `local_infer.py`
        tokenized = self.scoring_tokenizer(text,
                                           truncation=True,
                                           return_tensors="pt",
                                           padding=True,
                                           return_token_type_ids=False).to(self.args.device)
        labels = tokenized.input_ids[:, 1:]

        # evaluate text
        with torch.no_grad():
            logits_score = self.scoring_model(**tokenized).logits[:, :-1]
            if self.args.reference_model_name == self.args.scoring_model_name:
                logits_ref = logits_score
            else:
                tokenized = self.reference_tokenizer(text,
                                                     truncation=True,
                                                     return_tensors="pt",
                                                     padding=True,
                                                     return_token_type_ids=False).to(self.args.device)

                assert torch.all(
                    tokenized.input_ids[:, 1:] == labels), "Tokenizer is mismatch."  # NOQA: Unexpected types

                logits_ref = self.reference_model(**tokenized).logits[:, :-1]

            crit = self.criterion_fn(logits_ref, logits_score, labels)

        prob = self.prob_estimator.crit_to_prob(crit)
        # endregion

        return crit, prob


def test_as_local_infer(evaluator):
    log("Testing as local_infer.py")

    # region - Adapted from `local_infer.py`
    while True:
        # noinspection DuplicatedCode
        print("Please enter your text: (Press Enter twice to start processing)")
        lines = []
        while True:
            line = input()
            if len(line) == 0:
                break
            lines.append(line)
        text = "\n".join(lines)
        if len(text) == 0:
            break
        crit, prob = evaluator.evaluate(text)
        print(f'Fast-DetectGPT criterion is {crit:.4f}, '
              f'suggesting that the text has a probability of {prob * 100:.0f}% to be machine-generated.')
        print()
    # endregion
    print("Fin.")


def recv_n_bytes(sock, n):
    received_bytes = bytes()
    while len(received_bytes) < n:
        received_bytes += sock.recv(n - len(received_bytes))

    return received_bytes


def test(evaluator, ip, port, encoding):
    log("Starting client")

    sock = socket.socket()
    sock.settimeout(10)

    log(f"Attempting to connet to {ip}:{port}...")
    try:
        sock.connect((ip, port))
    except socket.gaierror:
        log("Address-related error connecting to server.")
        sock.close()
        return
    except socket.herror:
        log("Server-related error.")
        sock.close()
        return
    except socket.timeout:
        log("Connection timed out.")
        sock.close()
        return
    except socket.error as err:
        log(f"Connection error: {err}")
        sock.close()
        return
    log("Connected to server")
    sock.settimeout(None)

    while True:
        log("Waiting for communication")

        # Reading our communication id
        # 0 = terminate
        # 1 = text to be evaluated
        communication_id_bytes = recv_n_bytes(
            sock,
            struct.calcsize("!B")  # Unsigned char
        )
        communication_id, = struct.unpack("!B", communication_id_bytes)
        log(f"Received {communication_id = }")

        if communication_id == 0:  # Terminate message
            log("Terminate message received, closing socket")
            sock.close()
            return

        if communication_id != 1:
            log(f"Received unknown communication id {communication_id}, closing socket")
            sock.close()
            return

        # Next 4 bytes are message size
        message_length_bytes = recv_n_bytes(
            sock,
            struct.calcsize("!I")  # Unsigned integer
        )
        message_length, = struct.unpack("!I", message_length_bytes)
        log(f"Received {message_length = }")

        # Reading the message
        message_bytes = recv_n_bytes(
            sock,
            message_length
        )
        message = message_bytes.decode(encoding=encoding)
        log(f"Received {message = }")

        # Evaluate the message
        try:
            crit, prob = evaluator.evaluate(message)
        except Exception as e:
            log(f"Exception raised '{e}'")
            full_traceback = traceback.format_exc()
            log(f"Full traceback:\n{full_traceback}")
            raise e
        log(f"Calculated {crit = } and {prob = }")

        # Send the results back
        bytes_to_send = struct.pack(
            "!Bff",  # Unsigned char then two floats
            1, crit, prob
        )
        log(f"Sending {bytes_to_send = }")
        sock.sendall(
            bytes_to_send
        )


def main():
    log("Script started")

    # region - Adapted from `local_infer.py`
    # noinspection DuplicatedCode
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference_model_name', type=str,
                        default="gpt-neo-2.7B")  # use gpt-j-6B for more accurate detection
    parser.add_argument('--scoring_model_name', type=str, default="gpt-neo-2.7B")
    parser.add_argument('--dataset', type=str, default="xsum")
    parser.add_argument('--ref_path', type=str, default="./local_infer_ref")
    parser.add_argument('--device', type=str, default="cuda")
    parser.add_argument('--cache_dir', type=str, default="../cache")
    # endregion
    parser.add_argument("--test_as_local_infer", action="store_true")
    parser.add_argument("--ip", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=1737)
    parser.add_argument("--encoding", type=str, default="utf-8")
    args = parser.parse_args()

    log("Creating evaluator")
    evaluator = Evaluator(args)

    if args.test_as_local_infer:
        test_as_local_infer(evaluator)
    else:
        test(evaluator, args.ip, args.port, args.encoding)

    log("Fin.")


if __name__ == "__main__":
    main()
