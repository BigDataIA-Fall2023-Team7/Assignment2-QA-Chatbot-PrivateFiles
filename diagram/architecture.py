from diagrams import Diagram, Cluster, Edge, Node
from diagrams.custom import Custom
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.programming.language import Python
from diagrams.programming.framework import FastAPI

# Create a new diagram
with Diagram("Personal ChatBot Architecture", show=False, direction="LR", outformat="png") as diagram:
    
    # Define the user and Streamlit App
    with Cluster("User / Streamlit App"):
        user = Custom("User", "./images/user.png")
        app = Custom("Streamlit App", "./images/streamlit.png")

    # Define FastAPI and sub-processes
    with Cluster("PDF Processor"):
        fastapi = FastAPI("FastAPI")
        #validation = Python("Validation")
        NuogatAPIServer = Server("NuogatAPIServer")
        PyPDF=FastAPI("PyPDF on FastAPI")

    # Define the Model Creation process
    with Cluster("Model Creation"):
        create_model_api = FastAPI("/createModel API")
        fine_tuned_model = Python("Fine-tuned Model")

    # Define the ChatBot and endpoint
    with Cluster("ChatBot"):
        chat_bot = Custom("Personal ChatBot", "./images/streamlit.png")
        chat_answer_api = FastAPI("/getChatAnswer API")

    # Add connection links
    user >>Edge(label="PDF links")>> app
    app >> Edge(label="Request")>>fastapi #<< Edge(label="Processor is PyPDF")<< fastapi
    fastapi>>Edge(label="Processor=PyPDF") >> PyPDF
    fastapi>>Edge(label="Processor=Nougat")>>NuogatAPIServer
    NuogatAPIServer >>Edge(label=".mmd file")>> create_model_api
    PyPDF>>Edge(label=".mmd file")>>create_model_api
    create_model_api >> Edge(label="jsonl")>>fine_tuned_model>>chat_bot
    chat_bot >> Edge(label="Question")>>chat_answer_api
    chat_answer_api>>Edge(label="Answer")>>chat_bot