from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator
from deep_translator import GoogleTranslator
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, create_sql_query_chain

def transliterate_text(text, source_lang, target_lang):
    try:
        return UnicodeIndicTransliterator.transliterate(text, source_lang, target_lang)
    except Exception as e:
        print(f"Error in transliteration: {e}")
        return text

def extract_sql_query(template):
    answer_prompt = PromptTemplate.from_template(
        """You are a SQL query extractor. Given the noisy SQL template, extract the SQL query alone. Don't give anything else. Just extract the query and provide it as an answer.

        Noisy_query: {template}

        Answer: """
    )

    llm_model = ChatGroq(model="llama3-70b-8192", api_key='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')  # Replace with your actual API key
    llm = LLMChain(llm=llm_model, prompt=answer_prompt)
    ans = llm(inputs={"template": template})
    return ans["text"]

def Gen_Ai(questions, detected_language='en'):
    translator = GoogleTranslator()

    if detected_language != 'en':
        translated_question = translator.translate(questions, source=detected_language, target='en')
    else:
        translated_question = questions

    llm_model = ChatGroq(model="llama3-70b-8192", api_key='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')  # Replace with your actual API key
    db = SQLDatabase.from_uri(r"sqlite:///C:\Users\ARULMURUGAN M\OneDrive\Desktop\ai\demo\DataBase.db")
    chain = create_sql_query_chain(llm_model, db)
    sql_query = chain.invoke({'question': translated_question})
    final = extract_sql_query(sql_query)
    result = db.run(final)

    answer_prompt = PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, generate a proper reply with a proper structure to give to the user. Don't give anything else except the answer.

        Question: {question}
        SQL Query: {query}
        SQL Result: {result}

        Answer: """
    )

    llm = LLMChain(llm=llm_model, prompt=answer_prompt)
    ans = llm(inputs={"question": questions, "query": sql_query, "result": result})

    if detected_language != 'en':
        final_answer = translator.translate(ans["text"], source='en', target=detected_language)
    else:
        final_answer = ans["text"]

    return final_answer, result
