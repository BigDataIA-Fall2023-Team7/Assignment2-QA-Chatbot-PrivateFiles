# Assignment 2 : PDF Document Q&A Chatbot 

## Abstract
The PDF Document Summarization Q&A Chatbot is a specialized tool designed to help users extract and summarize information from PDF documents. This project aims to develop a tool for analysts to efficiently load PDF documents from the U.S. Securities and Exchange Commission (SEC) website and obtain summaries. The team is evaluating two possible libraries, Nougat and PyPDF, for text extraction. Additionally, the project draws inspiration from the Open AI cookbook to build a question and answer (Q&A) system based on books 2 and 3.

## Team Members 👥
- Aditya Kawale
  - NUID 002766716
  - Email kawale.a@northeastern.edu
- Nidhi Singh
  - NUID 002925684
  - Email singh.nidhi1@northeastern.edu
- Uddhav Zambare
  - NUID 002199488
  - Email zambare.u@northeastern.edu


## Project Structure
```text
backend
├── Pipfile
├── Pipfile.lock
├── README.md
├── example.env
├── fastapiservice
│   ├── __init__.py
│   ├── filecache
│   │   └── README.md
│   ├── postman
│   │   └── damg7245-assgn2-chatbot-private-files.postman_collection.json
│   ├── src
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── chatanswer.py
│   │   ├── processpdf.py
│   │   └── utilities
│   │       ├── __init__.py
│   │       └── customexception.py
│   └── test
│       ├── __init__.py
│       └── test_app.py
└── fine-tune model
    └── create-model.ipynb
```

```text
frontend
├── README.md
├── diagram
│   ├── architecture-assgn1-generator.py
│   └── architecture-assgn2-generator.py
├── images
│   ├── pdf_processing_flow.png
│   ├── qa_chatbot_for_pdfs_architecture.png
│   ├── streamlit.png
│   └── user.png
├── main.py
├── pages
│   ├── architecture-assign1.py
│   └── architecture-assign2.py
└── requirements.txt
```

## Links 📎
1. Nougat Library - [link](https://facebookresearch.github.io/nougat/)
2. SEC Forms - [link](https://www.sec.gov/forms)
3. PyPDF Documentation - [link](https://pypdf.readthedocs.io/en/stable/)
4. Open AI Cookbook - [link] (https://github.com/openai/openai-cookbook/tree/main/examples/fine-tuned_qa)
5. Streamlit - [link](https://streamlit.io/)

## Architecture 👷🏻‍♂️

![alt text](Architecture.png)

## Project Workflow

### Step 1: Input PDF URLs
- Users initiate the process by providing web links to PDF documents.
- The system validates and downloads the PDFs, saving them in cache memory for further processing.

### Step 2: Choose PDF Processor
- Users choose between PyPDF and Nougat for text extraction from the PDFs.

### Step 3: Create Sections of Processed PDF
- Text is segmented into coherent sections of approximately 1000 tokens.
- Sections are grouped and embedded for convenient access.

### Step 4: Generate a Model
- Select the "gpt-3.5-turbo-instruct" model for AI-based Q&A.
- Create question-answer pairs for model training.
- Format the data for fine-tuning and use the Open AI Finetuning Job API.

### Step 5: Chat with Your Personal Chatbot
- Users can interact with the fine-tuned model:
  - Provide a question.
  - The chatbot searches for relevant context.
  - Embeddings are generated and contexts ranked.
  - The top contexts are sent to the model for an answer, which is returned to the user.


## Steps to Execute

App can be directly accessed from Streamlit Cloud via [link](https://team7-a1-part2.streamlit.app/)

*OR*

1. **Clone the Repository**

    Clone the [repository](https://github.com/BigDataIA-Fall2023-Team7/Assignment1-PDF-Processing-Application.git) to your local machine:
   ```
   git clone <repository_url>
   ```

**Backend**

1. **Open the Backend folder**
    Navigate to the module directory:
   ```
   cd backend
   ```

2. **Create a .env file**
    Create a `.env` file with the necessary environment variables and API Keys. Reference: [example.env](example.env)

3. **Install Dependencies:**

   Open the terminal in VSCode and run the following commands:

   ```shell
   pipenv install --dev
   ```

4. **Activate Virtual Environment:**

   To activate the virtual environment, run:

   ```shell
   pipenv shell
   ```

5. **Run the Backend Server:**

   Start the backend server using Uvicorn. Run the following command:

   ```shell
   uvicorn fastapiservice.src.app:app --reload
   ```

   Your backend API will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

**Frontend**

1. **Open the Frontend folder**
    Navigate to the module directory:
   ```
   cd frontend
   ```

2. **Create a Virtual Environment:**
    Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. **Install Frontend Dependencies:**

   In the activated virtual environment, install the required Python packages:

   ```shell
   pip install -r requirements.txt
   ```

4. **Upgrade Pip (Optional):**

   You can upgrade Pip to the latest version if needed:

   ```shell
   pip install --upgrade pip
   ```

5. **Run the Frontend Application:**

   To start the frontend application, run the following command:

   ```shell
   streamlit run main.py
   ```

## Creating Your Own Fine-Tuned Language Model

1. Save a CSV file with 'context' and 'tokens' columns in the 'backend/fine-tune model' directory.
2. Open 'create-model.ipynb' in your Jupyter Notebook environment.
3. Modify the filepath in the first code snippet to point to your CSV file.
4. Follow the instructions in the notebook to fine-tune your model.


## Scope
This project expansion seeks to develop an organization-specific QA chatbot. This chatbot will allow businesses and institutions to effortlessly access and utilize internal documents by providing answers to company-specific questions. The key objectives include custom document integration, business-specific query responses, contextual understanding, knowledge retrieval automation, and user-friendly interactions. The workflow covers document integration, custom document processing, model training, user interactions, and continuous learning. This initiative promises efficient knowledge retrieval, consistent responses, increased productivity, scalability, and robust data security. 

## Contribution 🤝
*   Aditya : 34`%` 
*   Nidhi : 33`%`
*   Uddhav : 33`%`

## Individual Distribution ⚖️

| **Developer** |          **Deliverables**          	            |
|:-------------:|:-------------------------------------------------:|
|      Aditya   | Fast API Setup and Application deployment         |
|      Aditya   | Pdf text Segmentation and context creation        |
|      Uddhav   | Q&A dataset & Fine-tuning OpenAI model            |
|      Uddhav   | Answering questions by fetching related context   |
|      Nidhi    | Streamlit Front-End and API access point          |
|      Nidhi    | Data Research and Documentation                   |

---
---
> WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.
