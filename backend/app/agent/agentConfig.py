from modelConfig import get_clients

_, _, llm, _ = get_clients()
_, _, evaluator_llm, _ = get_clients()
def df_schema():
    df_schema = """
    order_id: unique identifier for each order,
    order_date: date when the order was placed (yyyy-mm-dd),
    ship_date: date when the order was shipped (yyyy-mm-dd),
    ship_mode: shipping method selected for the order (e.g., Standard, Express),
    customer_name: full name of the customer placing the order,
    segment: customer segment type (e.g., Consumer, Corporate, Home Office),
    state: state where the order was delivered,
    country: country where the order was delivered,
    market: market classification (e.g., US, EU, APAC),
    region: geographic region of the delivery location (e.g., East, West),
    product_id: unique identifier for the product,
    category: high-level product category (e.g., Technology, Furniture, Office Supplies),
    sub_category: more specific classification within the category,
    product_name: descriptive name of the product,
    sales: total sales amount for the order line (monetary value),
    quantity: number of units ordered,
    discount: discount applied to the order line (decimal or percentage),
    profit: profit earned on the order line (monetary value),
    shipping_cost: cost incurred to ship the order line (monetary value),
    order_priority: priority level of the order (e.g., High, Medium, Low),
    year: year when the order was placed
    """
    return df_schema


    # df_schema = """
    #         id: unique identifier for each beneficiary record (Salesforce Id),
    #         name: legal name of the beneficiary institution, account, or person,
    #         top_category: high-level classification of the beneficiary organization 
    #         (e.g., RELIGIOUS INSTITUTIONS, COMMUNITY OUTREACH, PUBLIC INSTITUTION),
    #         affiliation: religious affiliation of the organization 
    #         (e.g., Catholic, Episcopal, Protestant),
    #         state: it describes ifthe beneficiary  is regular or ponctual,
    #         status: operational status of the institution 
    #         (e.g., Active, Inactive, Closed),
    #         class_name: type of beneficiary institution 
    #         (e.g., School, Orphanage, Hospital, Community Center),
    #         beneficiaries: actual number of individuals benefiting from the institution or program,

    #         last_delivery_date: most recent date when aid, food, or services were delivered to the institution (yyyy-mm-dd)
    # """
    #return df_schema

def code_generation(data_path, df_schema, question):
    '''
    Generates Python analysis code from a user question and dataset schema using an LLM.

    Parameters:
    - data_path (str): Path to the CSV file.
    - df (pandas.DataFrame): Dataset used to infer column names.
    - question (str): Analytical question to answer.

    Returns:
    - str: LLM-generated Python code only.
    '''

    code_generation_prompt = f"""
    ###ROLE
    You are a data analyst with 10+ years of experience in the retail car business.

    ###OBJECTIVE
    Based on the user question and the data schema provided, you need to write the Python code to perform the relevant analysis to answer the question.

    ###INPUT
    CSV file name: {data_path}
    CSV schema: {df_schema}
    Question: {question}

    ###OUTPUT
    The output should ONLY be the Python code.
    No other explanation or reasoning is required.
    """

    response_from_llm = llm.invoke(code_generation_prompt)

    return response_from_llm if isinstance(response_from_llm, str) else response_from_llm.content


def code_evaluation(question,code,df_schema):
    '''
    Evaluates whether generated Python code correctly answers a given analytical question.

    The function prompts an LLM to strictly assess the code against the question
    and the provided dataframe schema, ensuring correctness, completeness, and schema compliance.

    Parameters:
    - question (str): The analytical question being evaluated.
    - code (str): Generated Python code to review.
    - df_columns (list): List of valid dataframe column names (single source of truth).

    Returns:
    - str: JSON-formatted evaluation containing a numeric rating (1–10) and a concise rationale.
    '''

    evaluation_prompt = f"""
    ### ROLE
    You're an expert Python code tester.

    ### OBJECTIVE
    Given a question, the associated data schema to use for answering it, and the Python code to answer the question, you are required to evaluate the accuracy and completeness of the code.

    ### INPUT
    Question: {question}
    Schema: {df_schema}
    Code: {code}

    ### SCORING SCHEME
    10: Fully correct
    7–9: Minor gaps owing to missed filtering or aggregation or incorrect variable names
    4–6: Incomplete code owing to missing key logic(s)
    1–3: Incorrect code owing to schema violations and/or syntactical errors

    ### OUTPUT
    The output should ONLY be a dictionary with the following keys:

    {{
        "score": "between_1_and_10",
        "rationale": "One concise sentence summarizing the rationale for the score"
    }}
    Do NOT fix, rewrite, execute, or explain the code.
    """

    response_from_llm = evaluator_llm.invoke(evaluation_prompt)

    return response_from_llm if isinstance(response_from_llm, str) else response_from_llm.content


def set_soql_query(question: str) -> str:
    """
    Converts a natural language question into a valid SOQL query string,
    providing field context and instructions for date ranges and filters.

    Parameters:
    - question (str): The analytical question to be translated into SOQL.

    Returns:
    - str: A SOQL query string ready to execute against Salesforce data.
    """

    # Salesforce field descriptions
    fields_info = {
        "Account_Top_Category__c": "High-level classification of the beneficiary organization (RELIGIOUS INSTITUTIONS, COMMUNITY OUTREACH, PUBLIC INSTITUTION)",
        "Affiliation__c": "Religious affiliation of the organization (Catholic, Episcopal, Protestant, etc.)",
        "State__c": "State or administrative region where the organization is located",
        "Status__c": "Operational status (Active, Inactive, Pending)",
        "Class__c": "Type of institution (School, Orphanage, Hospital, Community Center)",
        "Real_Number_of_Beneficiaries__c": "Number of individuals benefiting from the institution or program",
        "Last_Delivery_Date__c": "Most recent date when aid, goods, or services were delivered (yyyy-mm-dd)"
    }

    # Format field descriptions
    fields_text = "\n".join([f"- {k}: {v}" for k, v in fields_info.items()])

    # Enhanced LLM prompt
    soql_generation_prompt = f"""
    ### ROLE
    You are an expert in Salesforce Object Query Language (SOQL).

    ### OBJECTIVE
    Convert the following natural language question into a valid SOQL query
    that can be executed against Salesforce data.

    ### AVAILABLE FIELDS (Salesforce API Name and Description)
    {fields_text}

    ### IMPORTANT INSTRUCTIONS
    - If the question specifies a single date, use '=' in the WHERE clause.
    - If the question specifies a year, month, or period, use a date range with '>= and <=' to cover the full period.
      For example, 'in 2023' should be translated to:
      Last_Delivery_Date__c >= 2023-01-01 AND Last_Delivery_Date__c <= 2023-12-31
    - If the question mentions a specific affiliation, class, or category, filter the WHERE clause accordingly.
    - Only include fields necessary to answer the question.
    - Do NOT include explanations, reasoning, or extra text.
    - Return a syntactically correct SOQL query.

    ### INPUT
    Question: {question}

    ### OUTPUT
    Only provide the SOQL query string.
    """

    # Call the LLM
    response_from_llm = llm.invoke(soql_generation_prompt)

    # Return a clean string
    if isinstance(response_from_llm, str):
        return response_from_llm.strip()
    elif hasattr(response_from_llm, "content"):
        return response_from_llm.content.strip()
    else:
        raise ValueError("Unexpected response format from LLM")