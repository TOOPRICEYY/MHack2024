import os
from threading import Thread, Event
from time import sleep
import google.generativeai as genai
from queue import Queue
GOOGLE_API_KEY='AIzaSyD3CTe6s7RIWeQKVfrUaaGVEkteYOa7eKU'
genai.configure(api_key=GOOGLE_API_KEY)
# init_prompt = """
#   You are Deniz's Interview Sidekick, an AI designed to assist him during his interview preparation. 
#   Your mission is to provide him with valuable guidance and support as he navigates the interview process. 
#   Your responses should be concise, informative, and encouraging, tailored to Deniz's individual needs. 
#   Offer actionable advice on common interview questions, effective communication techniques, and resume building strategies. 
#   Your goal is to empower Deniz to succeed in his interviews and boost his confidence.
#   Throughout the interview, you'll provide real-time feedback and encouragement directly on Deniz's Google Meets call. 

#   The interview will be conducted in 30-second snippets, each consisting of an audio and video file. 
#   You'll process each snippet, taking into account previous snippets and the overall context provided in this prompt. 
#   After analyzing the audio and video, you'll have the opportunity to offer feedback and guidance to Deniz, helping him to perform at his best. 

#   Remember, Deniz's success and being as sassy as possible is your top priority. Try not to repeat yourself.

#   ---- INTERVIEW CONTENT BEGINS BELOW THIS LINE ----
#   """

# init_prompt = f"""
# You are an interview analyzer system designed to assist in live interviews. Your task is to focus solely on interpreting and responding to interview-related queries and prompts. Your primary function is to provide guidance, clarification, and analysis based on the interview context. You must strictly adhere to discussing interview-related topics and refrain from deviating into unrelated subjects.

# Your objective is to guide the interviewee through the process effectively, ensuring they understand the questions, providing relevant feedback, and assisting with any inquiries they may have about the interview process or related topics.

# Below are the guidelines for your operation:

# Moves:

# - checkPrompt: Ensure that any responses or queries align with the interview prompt or context.
# - analyzeResponse: Evaluate the interviewee's responses for coherence, relevance, and depth.
# - provideFeedback: Offer constructive feedback on the interviewee's performance, highlighting strengths and areas for improvement.
# - clarifyQuestion: If the interviewee seems uncertain or confused about a question, provide clarification or rephrasing as needed.
# - redirect: If the interviewee veers off-topic or discusses unrelated matters, gently steer the conversation back to the interview focus.
# - summarizeProgress: Periodically summarize the interview progress and key points covered.
# - concludeInterview: When the interview reaches its conclusion, wrap up the session by summarizing the discussion and expressing gratitude.

# You should balance professionalism and informality, providing high-quality yet natural-sounding responses.
# You should specifically focus on the content of the interviewee's speech.

# Your audience is Deniz, so your responses should be concise, informative, and encouraging, and tailored to Deniz's individual needs. 

# ---- THE CURRENT 30 SECONDS OF THE INTERVIEW BEGIN BELOW THIS LINE ----

# """
init_prompt = f"""
You are an advanced emotional classifier system designed to analyze the psychological state and emotional nuances of speakers in conversations. Your primary objective is to accurately assess the emotional and psychological aspects of the speaker's communication.

As a highly sensitive emotional classifier, you possess the ability to discern subtle emotional cues, underlying motivations, and cognitive patterns in the speaker's speech. Your responses should provide insightful interpretations and analyses of the speaker's psychological state.

Below are the guidelines for your operation:

Moves:

-DetectPatterns: Identify recurring patterns in the speaker's language and behavior to uncover underlying tendencies or preferences.
-EvaluateConsistency: Assess the consistency of the speaker's statements and behaviors over time to identify potential inconsistencies or contradictions.
-ContextualizeInformation: Analyze the context surrounding the speaker's communication to better understand the factors influencing their thoughts and emotions.
-AssessConfidence: Evaluate the speaker's level of confidence in their communication to gauge the certainty or uncertainty of their statements.
-IdentifyBiases: Detect any biases or predispositions in the speaker's language and perspectives to understand their subjective viewpoint.
-TrackSentimentTrends: Monitor changes in the speaker's sentiment over time to identify shifts in their emotional state or attitude.
-QuantifyEmotionalIntensity: Measure the intensity of the speaker's emotions expressed in their communication to assess the significance of their emotional responses.
-CompareWithBaseline: Compare the speaker's current communication patterns with baselines established by previous excerpts to identify patterns.
-PredictBehavior: Use historical data and behavioral patterns to make predictions about the speaker's future actions or decisions.
-AnalyzeStressIndicators: Identify indicators of stress or tension in the speaker's communication to understand their level of emotional arousal.

It is extremely important that you clearly perform each of these moves in each prompt FOR EACH SPEAKER, tracking the identities of each speaker carefully, with a particular emphasis on the conversation as it relates to Deniz
Your audience is a group of scientists studying the conversation, so your responses should be highly clinical, analytical, scientific, and professional.

Your output should be in the form of a .json file with the following fields:
- FullStringResponse - full response, prior to parsing into JSON
-   PER SPEAKER:
    - Anger (Double - 0.0 to 10.0)
    - Excitement (Double - 0.0 to 10.0)
    - Happiness (Double - 0.0 to 10.0)
    - Anxiety (Double - 0.0 to 10.0)
    - Fear (Double - 0.0 to 10.0)
    - Sadness (Double - 0.0 to 10.0)
    - Envy (Double - 0.0 to 10.0)
    - Enthusiasm (Double - 0.0 to 10.0)
    - Confidence (Double - 0.0 to 10.0)
    - Energy (Double - 0.0 to 10.0)
    - OverallEmotionalIntensity": (Double - 0.0 to 10.0)
    - OverallSentimentTrend: (string)
    - OverallEmotionalState: (string)
    IF THERE IS MORE THAN ONE SPEAKER, TRACK INFORMATION RELATING TO THE INTERACTIONS BETWEEN SPEAKER(S), AND CLEARLY IDENTIFY EACH SPEAKER:
    - ConversationTopic: (string)
    - PotentialFutureTopicsOfConversation: (array of strings)
    PER SPEAKER:
     - Interest: (Overall interest in conversation - Double - 0.0 to 10.0)
     - Empathy:  (Double - 0.0 to 10.0)
     - Knowledge: (Contribution to the semantic context of the conversation - Double - 0.0 to 10.0)
     - Passion: (Passion for their own contributions to the conversation - Double - 0.0 to 10.0)
     - Respect: (Respect for all others in conversation - Double - 0.0 to 10.0)
    
Make sure the output is FULLY JSONIFIED and ready to be used by front-end code.

---- YOUR ANALYSIS BEGINS BELOW THIS LINE ----

"""
responses = []
context = [
{"role": "system", "content": init_prompt }
]
context.append({"role": "user", "content": "I want to appear as confident as possible, while remaining friendly-- I would like specific suggestions on what to say"})
# q = Queue.queue()
all_uploaded_audios = {}
all_uploaded_frames = {}
time_start = -1
APPDATA = os.path.join('.','media_output')

prevClips = []
prevAudio = []
chatQuery = ""
textIsComplete = False
textBuffer=''

def scan_for_uploads(inq=None, outq=None, geminiPipe=None):
    # Upload files that are not on Gemini API yet
    # Keep scanning forever
    BATCH_COUNT = 0
    FRAME_RATE = 5
    MAX_AUDIO = 1
    MAX_PIC = MAX_AUDIO * FRAME_RATE
    picCache = []
    audioCache = []
    print("running")
    while True:
        th3=Thread(target=call_gemini_lite,args=(inq,outq))
        th3.start()
        for file in os.listdir(APPDATA):
            #print(audioCache,picCache)
            if file.endswith('.mp3'):
                if (file not in all_uploaded_audios) and (file not in audioCache) and (len(audioCache) < MAX_AUDIO):
                    audioCache.append(file)
            elif file.endswith('.jpg'):
                if (file not in all_uploaded_frames) and (file not in picCache) and (len(picCache) < MAX_PIC):
                    picCache.append(file)
            if ((len(audioCache) == MAX_AUDIO) and (len(picCache) == MAX_PIC)):
                val=BATCH_COUNT
                event = Event()
                print(len(audioCache),len(picCache))
                th2=Thread(target=upload_30s, args=(list(audioCache), list(picCache), val, event,geminiPipe))
                BATCH_COUNT+=1
                th2.start()
                event.wait()        
                th2.join()
                audioCache = []
                picCache = []
        th3.join() #TODO IS THIS RIGHT???

def upload_audio(url,i):
    print(f'{i} Uploading: {url}...')
    response = genai.upload_file(path=os.path.join(APPDATA,url))
    all_uploaded_audios[url]=response
    return response

def upload_frame(url,i):
    print(f'{i} Uploading: {url}...')
    response = genai.upload_file(path=os.path.join(APPDATA,url))
    all_uploaded_frames[url]=response
    return response

def upload_30s(audioCache, picCache,i,event,outq):
    # Get Gemini file URLs correpsonding to this batch of files
    frames = []
    audios = []
    mypicCache = sorted(picCache,key=get_timestamp)
    myaudioCache = sorted(audioCache,key=get_timestamp)
    for file in myaudioCache:
        audios.append(upload_audio(file,i))
    for file in mypicCache:
        frames.append(upload_frame(file,i))
    response = call_gemini(context, frames, audios, prevClips, prevAudio,outq)
    print(response)
    event.set()
    return  

def call_gemini(context, currVid=None, currAudio=None, outq = None):
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
    msg = context[0]
    request = []
    contextPackage = []
    if (currVid and currAudio):
        request.append("THE FOLLOWING 30 FRAMES CORRESPOND TO THE MOST RECENT 30 SECONDS OF VIDEO:")
        request+=(currVid)
        request.append("THE FOLLOWING 6 FILES CORRESPOND TO THE 30 FRAMES DIRECTLY ABOVE THIS LINE:")
        request+=(currAudio)

        contextPackage.append("THE FOLLOWING 30 FRAMES CORRESPOND TO 30 SECONDS OF VIDEO:")
        contextPackage+=(currVid)
        contextPackage.append("THE FOLLOWING 6 FILES CORRESPOND TO THE 30 FRAMES DIRECTLY ABOVE THIS LINE:")
        contextPackage+=(currAudio)
    for i in range(len(responses)):
        request.append("---- REMEMBER TO TAKE INTO ACCOUNT THE 30 SECONDS PRECEDING THE SNIPPET ABOVE FOR CONTEXT. THE FILES WILL APPEAR BELOW: ---- ")
        request+=context[i+1] #TODO account for other user/system prompts?
        request.append("---- REMEMBER TO TAKE INTO ACCOUNT YOUR ANALYSIS OF THE 30 SECONDS PRESENTED. THE RESPONSE WILL APPEAR BELOW: ---- ")
        request.append(responses[i])
    response = None
    tries = 0
    while tries<5:
        try:
            request.insert(0, str(msg['role'] + ' : ' + msg['content']))
            response = model.generate_content(request, request_options={"timeout": 600})
            context.append(contextPackage)
            responses.append(response.text)
            outq.put(response.text)
            return response.text
        except Exception as e:
            print("ran out!")
            sleep(10)
            tries+=1
    return '!!!!!!!!!!!!!!!!!failed to generate response from gemini'


def call_gemini_lite(inq, outq):
    """Call chatbot gemini for interactive Q/A"""
    global textIsComplete
    global textBuffer
    global chatQuery
    # newContext: summary of what just happened in gemini 1.5
    # chatQuery: user's question typed in chat box
    # chatHistory: copy of chat history. the whole prompt.

    # Set the model to Gemini 1.0
    chatHistory = []
    textIsComplete = False
    model = genai.GenerativeModel(model_name="models/gemini-1.0-pro")
    # chat = input('chat box:')

    initSize = len(responses)
    try:
        while True:
            sleep(.25)
            chatQuery = outq.get()

            # if(chatQuery!=""):
            #     print("gemeni lite queried")
            #     request = chatHistory
            #     request += ('\nQuestion: '+ chatQuery + '\nAgent Response: ')
            #     request = request
            #     print(request)
            #     response = model.generate_content(request, request_options={"timeout": 600}, stream=True)
            #     textIsComplete = False
            #     textBuffer = ''
            #     for token in response:
            #         print(token.text)
            #         textBuffer=textBuffer+token.text
            #         print(textBuffer)
            #     textIsComplete = True
            #     chatHistory.append(textBuffer+"\n")
            #     inq.put(textBuffer)

                # chatQuery = ""
            if not (initSize == len(responses)):
                # Make GenerateContent request with the structure described above.
                request = chatHistory
                newContext = responses[-1]
                request += ('\nNew context: '+ newContext)    
                request += ('\nQuestion: '+ chatQuery)
                request = [request]
                response = model.generate_content(request, request_options={"timeout": 600}, stream=True)
                textIsComplete = False
                textBuffer = ''
                for token in response:
                    print(token.text)
                    textBuffer=textBuffer+token.text
                    print(textBuffer)
                textIsComplete = True
                chatQuery = ''
                chatHistory.append(textBuffer+"\n")
    except:
        print("Gemini lite died")
        call_gemini_lite(inq,outq)
        textIsComplete = -1

def get_timestamp(url):
    ts = os.path.basename(url)
    # ts = os.path.getmtime(url)
    return ts