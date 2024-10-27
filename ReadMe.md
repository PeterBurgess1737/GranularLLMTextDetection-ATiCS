# Advanced Topics in Computer Science Project

# Addressing Granularity in LLM Text Detection

By Peter Burgess

<!-- TOC -->
* [Advanced Topics in Computer Science Project](#advanced-topics-in-computer-science-project)
* [Addressing Granularity in LLM Text Detection](#addressing-granularity-in-llm-text-detection)
  * [Setup.](#setup)
    * [Main file environment](#main-file-environment)
    * [AI Text Detector](#ai-text-detector)
      * [Fast-DetectGPT](#fast-detectgpt)
        * [Setting up the Virtual Environment](#setting-up-the-virtual-environment)
          * [Testing](#testing)
        * [Setting up the Scripts](#setting-up-the-scripts)
          * [Testing](#testing-1)
    * [Data](#data)
  * [Execution](#execution)
<!-- TOC -->

## Setup.

Please note that I used Windows 11 to run this project

### Main file environment

I used Pyhon 3.12 for the main script.  
Requirements can be installed with `pip install -r requirements.txt`.

The OpenAI API is used and requires an api key.  
Once can be generated here https://platform.openai.com/organization/api-keys.  
In the root directory, a file called `api_key.txt` is expected where the api key should be placed.

Please note that using the OpenAI API costs money, priced per token.  
However, the amount of tokens used here, if parameters remain unchanged, is rather small due to time constraints, and
should not set you back more than \$1.  
I spent something like \$3.15 which included multiple runs with different window sizes and testing.

### AI Text Detector

I have tested with the Fast-DetectGPT detector.

#### Fast-DetectGPT

Clone the repository: `git clone https://github.com/baoguangsheng/fast-detect-gpt.git`

It requires Python 3.8 and the packages installed with its own requirements.txt file.  
This project assumes a Python 3.8 virtual environment is set up in the same directory.

##### Setting up the Virtual Environment

The following commands assume you are still in this repository.

To set up this virtual environment:

1. Create the virtual environment:  
   `py -3.8 -m venv .\fast-detect-gpt\.venv-py3.8\`
2. Activate the virtual environment:  
   `.\fast-detect-gpt\.venv-py3.8\Scripts\activate`
3. Install the requirements:  
   `pip install -r .\fast-detect-gpt\requirements.txt`
4. Install a forgotten requirement:  
   `pip install scikit-learn`
5. Reinstall pytorch with cuda (not strictly necessary):  
   `pip uninstall torch`  
   See https://pytorch.org/get-started/locally/, select the necessary details and run the given command.  
   I used: Stable (2.4.1), Windows, Pip, Python, CUDA 12.4
6. Deactivate the virtual environment:  
   `deactivate`

###### Testing

You can test if this was set up properly by:

1. Activating the virtual environment:  
   `.\fast-detect-gpt\.venv-py3.8\Scripts\activate`
2. Changing directory:  
   `cd .\fast-detect-gpt\`
3. Running the local inference script:  
   `python .\scripts\local_infer.py`  
   This will take some time as it needs to download model weights.  
   Add `--device cpu` if you do not wish to use cuda.
4. Provide some text input and receive a percentage chance of it being AI generated.

Entering nothing closes the program.  
Remember to return to the main directory.

##### Setting up the Scripts

Run the setup_fast-detect-gpt.py file:  
`python .\scripts\fast_detect_gpt_setup.py`

###### Testing

You can test if this was set up properly by:

1. Activating the virtual environment:  
   `.\fast-detect-gpt\.venv-py3.8\Scripts\activate`
2. Changing directory:  
   `cd .\fast-detect-gpt\`
3. Running the client script as if it were the local infer script:  
   `python .\scripts\client_fast-detect-gpt.py --test_as_local_infer`  
   This will take some time as it needs to download model weights.  
   Add `--device cpu` if you do not wish to use cuda.
4. Provide some text input and receive a percentage chance of it being AI generated.

Entering nothing closes the program.  
Remember to return to the main directory.

### Data

I used a subset of the Human texts found here https://www.kaggle.com/datasets/starblasters8/human-vs-llm-text-corpus.  
The data should be downloaded and extracted under `/data/original` and the folder renamed to
`Human vs LLM Text Corpus`.  
Two are two main files that are expected:

1. `/data/original/Human vs LLM Text Corpus/data.csv`
2. `/data/original/Human vs LLM Text Corpus/prompts.csv`

This data was then used to generate a subset and mix in LLM modified/generated sentences amongst the human ones.  
The method used to generate this subset can be found in `preparing_data.ipynb`.

## Execution

Execution is performed via a series of Jupyter Notebook files.

First the data needs to be prepared.  
This includes the extraction of the human texts and introduction of LLM sentences.

Three Jupyter Notebooks were made for this.

1. [preparing_data_1.ipynb](preparing_data_1.ipynb)
2. [preparing_data_2.ipynb](preparing_data_2.ipynb)
3. [preparing_data_3.ipynb](preparing_data_3.ipynb)

The major differences between these three is the prompt used to modify the texts.  
That, and there was a major refactor going from 1 to 2.

I would recommend using [preparing_data_3.ipynb](preparing_data_3.ipynb) as it is the one that had the most time spent
on development.

This creates a series of json files in the `/data/prepared` directory that contain the LLM modified texts and the
unchanged texts.  
The individual sentences are also in these json files, alongside a bunch of boolean flags indicating if the sentence was
touched by an LLM.

Next we move onto evaluating the data.  
This is done through the notebook [evaluating_data.ipynb](evaluating_data.ipynb).  
Here each of the texts are sent to a LLM detector model to get predictions on the likelihood of it being LLM
generated.  
The results are saved in the `/data/evaluated` directory.  
Then a working set of texts is created.  
This is done by taking an equal amount of human only and LLM modified texts and placing them in the `/data/working_set`
directory.  
Within which there are two subdirectories `fine_tuning_set`, used to select thresholds for a final verdict, and
`/evaluation_set`, used to assess the correctness of the thresholds.

Finally, we have the last two Jupyter Notebooks.

1. [roc_with_simple_analysis.ipynb](roc_with_simple_analysis.ipynb)
2. [roc_with_majority_vote.ipynb](roc_with_majority_vote.ipynb)

These use the data in the `/data/working_set` directory to select an optimal threshold and then evaluate the selected
threshold.  
Two methods are used, a simple analysis, which uses simple statistical functions to generate a verdict, and a majority
vote, which uses a more brute force approach.

Running these will save some graphs and text files in the `/data` directory that contain the results.

Please note that running any of the notebooks will destroy any data previously in that directory, apart from
`/data/original`.  
If there is data you wish you keep, then move the contents of the `/data` directory.  
However, the subdirectories, `/data/prepared`, `/data/evaluated` and `/data/working_set` must remain, although their
contents can be removed.  
The scripts expect them to exist.
