from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import os
PDF_FILE_PATH = r'C:\Users\rabid\Desktop\internship\django\Qwerty Experts Policies 2024.pdf'
#chatbot
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import time
from langchain.prompts import ChatPromptTemplate
from langchain.globals import set_llm_cache, get_llm_cache
from langchain.globals import set_verbose, get_verbose
from langchain.globals import set_debug, get_debug
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")  # Adjust the URI
db = client["QwertyExperts"]
collection_employee = db["employee_data"]
load_dotenv()

# Create your views here.

def fetch_employee_data(query):
    # Perform the query on the relevant fields in your MongoDB collection
    results = collection_employee.find({
        "$or": [
            {"Employee Name": {"$regex": query, "$options": "i"}},
            {"Status": {"$regex": query, "$options": "i"}}
        ]
    })

    data = []
    for result in results:
        # Format the result to include every detail from the record
        formatted_result = (
            f"Employee Name: {result.get('Employee Name', 'N/A')}, "
            f"Status: {result.get('Status', 'N/A')}, "
            f"Availed Leaves (Annual): {result.get('Availed Leaves Annual Leaves', 'N/A')}, "
            f"Availed Leaves (Casual): {result.get('Availed Leaves Casual Leaves', 'N/A')}, "
            f"Availed Leaves (Sick): {result.get('Availed Leaves Sick Leaves', 'N/A')}, "
            f"Availed Leaves (WFH): {result.get('Availed Leaves WFH', 'N/A')}, "
            f"Availed Leaves (Extra): {result.get('Availed Leaves Extra', 'N/A')}, "
            f"Allocated Leaves (Annual): {result.get('Allocated Leaves Annual', 'N/A')}, "
            f"Allocated Leaves (Casual): {result.get('Allocated Leaves Casual', 'N/A')}, "
            f"Allocated Leaves (Sick): {result.get('Allocated Leaves Sick', 'N/A')}, "
            f"Allocated Leaves (WFH): {result.get('Allocated Leaves WFH', 'N/A')}, "
            f"Allocated Leaves (Extra): {result.get('Allocated Leaves Extra', 'N/A')}, "
            f"Remaining Leaves (Annual): {result.get('RemainingAnnual', 'N/A')}, "
            f"Remaining Leaves (Casual): {result.get('Remaining Casual', 'N/A')}, "
            f"Remaining Leaves (Sick): {result.get('Remaining Sick', 'N/A')}, "
            f"Remaining Leaves (WFH): {result.get('Remaining WFH', 'N/A')}, "
            f"Remaining Leaves (Extra): {result.get('Remaining Extra', 'N/A')}, "
    
        )
        data.append(formatted_result)

    # Return all formatted data or a fallback message if no data is found
    return " | ".join(data) if data else "No relevant information found in the database."

@login_required(login_url='Login')
def chatbot(request):
    
    if request.method == 'POST':
        query = request.POST.get('query', '')
        cache = get_llm_cache()
        set_llm_cache(cache)
        set_verbose(True)
        set_debug(True)

        # Initialize LangChain components
        llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="Llama3-8b-8192")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        memory = ConversationBufferMemory()
        
        loader = PyPDFDirectoryLoader("./data")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.split_documents(docs[:20])
        vectors = FAISS.from_documents(final_documents, embeddings)

        # Get employee data
        employee_data = fetch_employee_data(query)
        context = employee_data

        prompt_template = ChatPromptTemplate.from_template(
             """If the question is general, such as:
            - "Hi"
            - "Hello"
            - "How are you?"
            - "What’s up?"
            - "Can you help me?"
            - "What’s your name?"
            - "Tell me a joke."
            - "What time is it?"
            - "Where are you located?"
            - "How do I contact support?"
            - "What is your purpose?"
            - "Can you tell me about yourself?"
            - "What can you do?"
            - "How can I get started?"
            - "What are your hours of operation?"
            - "What is your favorite color?"
            - "Do you have any recommendations?"
            - "Can you provide some information?"
            - "How do I use this service?"
            - "What are the latest updates?"
            - "Can you explain something to me?"
            - "What’s new?"
            - "Do you have any news?"
            - "Who are you?: I am QWERTY Experts HR representative chatbot"
            - "What’s the best way to reach you?"
            -"what is my name":
            
            Provide a friendly and relevant response for these questions.
            
            If the question is specific to the provided context, answer it based on the context only. Please provide the most accurate response based on the question. If an answer cannot be found in the context, provide the closest related answer.
            if user ask about name, answer it by proving login user name :{name}.
             
            
            <context>
            {context}
            <context>
            Questions: {input}"""
        )
        document_chain = create_stuff_documents_chain(llm, prompt_template)
        retriever = vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        # Create conversation chain with memory
        conversation = ConversationChain(llm=llm, verbose=True,memory=ConversationBufferMemory())

        start = time.process_time()
        response = retrieval_chain.invoke({'input': f"{query}\n{memory.buffer}", 'context': f"{context}\n{memory.buffer}", 'name': request.user.username})
        response_time = time.process_time() - start
        
        conversation.predict(input=query)
#       
        memory.save_context({'input': query}, {'outputs': response['answer']}) 
        memory.load_memory_variables({})
        #
        subject = "HR Assistance Request"
        email_body = f"I am {request.user.username} \n\n{response['answer']}\n\nBest regards,\n{request.user.username}"

        # Prepare bot message
        bot_message = f"<p><strong>🤖:</strong> {response['answer']}</p>"

        # Check if the query involves sending an email
        if 'send email' in query.lower() or 'email' in query.lower():
            # Ask the user for confirmation to send the email
            bot_message += "<p><strong>🤖:</strong> Would you like to send this email? Please type 'yes' or 'no'.</p>"
            request.session['pending_email'] = {
                'subject': subject,
                'body': email_body,
                'recipient': ['abdullahaftab.itx@gmail.com']  # Replace with actual recipient
            }

        # If the user confirms with "yes," send the email
        elif 'yes' in query.lower() and request.session.get('pending_email'):
            pending_email = request.session.pop('pending_email', None)
            if pending_email:
                email = EmailMessage(
                    subject=pending_email['subject'],
                    body=pending_email['body'],
                    from_email='pythonsqwerty@gmail.com',  
                    to=pending_email['recipient'],
                )
                email.send()

                # Notify the user that the email has been sent
                bot_message = "<p><strong>🤖:</strong> Your email has been sent to HR.</p>"

        # Add user and bot messages to chat history
        chat_history = request.session.get('chat_history', [])
        user_message = f"<p><strong>🙎 {request.user.username}:</strong> {query}</p>"
        chat_history.append(user_message)
        chat_history.append(bot_message)
        request.session['chat_history'] = chat_history

        return render(request, 'chatbot.html', {'chat_history': chat_history})

    chat_history = request.session.get('chat_history', [])
    return render(request, 'chatbot.html', {'chat_history': chat_history})

    #return render (request,'home.html')
#
def Signuppage(request):
    if request.method=='POST':
        username1=request.POST.get('username')
        useremail=request.POST.get('email')
        userpass=request.POST.get('password1')
        userpass2=request.POST.get('password2')
        if userpass!=userpass2:
            return HttpResponse ("user password does not match")
       # if User.objects.filter(username=username1).exists():
        #    return HttpResponse("Username already exists. Please choose a different one.")
        else:
            my_user=User.objects.create_user(username1,useremail,userpass)
            my_user.save()
             # Send signup confirmation email
            subject = 'Welcome to Our Platform'
            message = f'Hi {username1},\n\nThank you for signing up at our platform. We hope you have a great experience!\n\n Please find your welcome PDF attached'
            from_email = 'pythonsqwerty@gmail.com'  # You can also use DEFAULT_FROM_EMAIL from settings
            recipient_list = [useremail]
            email = EmailMessage(
                subject,
                message,
                from_email,
                recipient_list,
            )
            if os.path.exists(PDF_FILE_PATH):
                email.attach_file(PDF_FILE_PATH)
            else:
                return HttpResponse("PDF file not found.")

            email.send()
            #send_mail(subject, message, from_email, recipient_list)
        return redirect('Login')
                   
    return render (request,'signup.html')

def loginpage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('chatbot')
        else:
            return HttpResponse("Username or Password is incorrect")
            
        
    return render(request,'login.html')
def logoutpage(request):
    
    logout(request)
    return redirect('Login')