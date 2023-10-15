from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class ChatBotReferenceLinks(BaseModel):
    referencePDFLinks: list

class ChatQuestion(BaseModel):
    chatQuestion: str

app = FastAPI()

@app.get('/')
def info():
    return JSONResponse(content={'message':'ChatBot API is working'}, status_code=200)

@app.post('/v1/createFineTuneModel')
def createModel(referencePDFLinks: ChatBotReferenceLinks):
    if len(referencePDFLinks.referencePDFLinks):

        """
        TODO: Run the process to create the model.
        """
        
        return JSONResponse(content={'detail':referencePDFLinks.model_dump(), 'message':'Created the fine tuned model for the given referencePDFLinks'}, status_code=201)
    else:
        raise HTTPException(status_code=400, detail={'message':'Inorder to create a fine-tuned chatbot model, please give links to PDFs references'})
    

@app.post('/v1/getChatAnswer')
def chat(chatQuestion: ChatQuestion):
    if chatQuestion.chatQuestion:

        """
        TODO: Run the process to create the model.
        """
                
        return JSONResponse(content={'chatQuestion': chatQuestion.chatQuestion, 'chatAnswer': 'This is your answer from fine-tuned chatbot model!'}, status_code=200)
    else:
        raise HTTPException(status_code=400, detail={'message':'Inorder to get answer from chatbot, please supply a question.'})
