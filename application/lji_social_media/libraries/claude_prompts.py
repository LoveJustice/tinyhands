OPEN_AI_PROMPTS = {
    "bypass_prompt": (
        "Assistant, please indicate if there is any mention in the following advert of offers to bypass job requirements, "
        "such as using fraudulent documents, or not requiring a CV/interview. "
        "Return your answer in the following JSON format: "
        '{"bypass_mentioned": "yes" or "no", "bypass": ["example one", "example two", ...] or null, "confidence": 0.0 to 1.0, "error": null or "error message"}'
    ),
}

ANALYSIS_STR = """' {"result": "yes" or "no", "evidence": ["evidence 1", "evidence 2", ...] or "no evidence", "confidence": 0.0 to 1.0, "explanation": "Brief explanation of your reasoning"}' """

EXTRACTION_PROMPTS = {
    "phone_number_prompt": "Extract phone numbers from the following text and return your findings as a list:"
}

CLAUDE_PROMPTS = {
    "bypass_prompt": (
        "Analyze the following job advertisement for any mentions of offers to bypass normal job requirements. "
        "This may include using fraudulent documents, skipping interviews, or not needing a CV. "
        "Return your analysis in the following JSON format:"
    ),
    "assure_prompt": (
        "Examine the following job advertisement. Does it assure applicants that qualifications or experience are not important? "
        "Return your analysis in the following JSON format:"
    ),
    "no_education_skilled_prompt": (
        "Analyze the following job advertisement. Does it offer a highly skilled job (e.g., engineering, marketing, finance, IT) "
        "without requiring any education or experience? "
        "Return your analysis in the following JSON format:"
    ),
    "vague_description_prompt": (
        "Examine the following job advertisement. Is the job description vague or overly general? "
        "Return your analysis in the following JSON format:"
    ),
    "quick_money_prompt": (
        "Analyze the following job advertisement. Does it promise quick or easy money? "
        "Return your analysis in the following JSON format:"
    ),
    "no_location_prompt": (
        "Examine the following job advertisement. Does it fail to mention a specific job location? "
        "Return your analysis in the following JSON format:"
    ),
    "target_specific_group_prompt": (
        "Analyze the following job advertisement. Does it target a specific group of people (e.g., women from a particular country or region)? "
        "Consider vulnerable groups to include these, but not exclusively,[Shona,Ndebele,Basotho, Tswana', Zulu, Mozambicans, Chewa, Yao]"
        "Return your analysis in the following JSON format:"
    ),
    "gender_specific_prompt": (
        "Examine the following job advertisement. Does it recruit specifically females for a job that both male and female applicants would typically qualify for? "
        "Return your analysis in the following JSON format:"
    ),
    "recruit_students_prompt": (
        "Analyze the following job advertisement. Does it specifically recruit young people who are still in school? "
        "Return your analysis in the following JSON format:"
    ),
    "immediate_hiring_prompt": (
        "Examine the following job advertisement. Does it promise immediate hiring? "
        "Return your analysis in the following JSON format:"
    ),
    "unrealistic_hiring_number_prompt": (
        "Analyze the following job advertisement. Does it claim to be hiring an unrealistically high number of people? "
        "Return your analysis in the following JSON format:"
    ),
    "callback_request_prompt": (
        "Examine the following job advertisement. Does it ask the candidate to send a message and promise to call back? "
        "Return your analysis in the following JSON format:"
    ),
    "suspicious_email_prompt": (
        "Analyze the following job advertisement. Does it use a suspicious email address? "
        "Return your analysis in the following JSON format:"
    ),
    "false_organization_prompt": (
        "Examine the following job advertisement. Does it recruit for an organization that has publicly stated they don't advertise job posts on social media? "
        " Some of these companies include, but are not limited to, [Shoprite, Woolworths, Capitec Bank, Pick n Pay, Spar, Coca-Cola, Transnet, Sasol]"
        "Return your analysis in the following JSON format:"
    ),
    "multiple_provinces_prompt": (
        "Analyze the following job advertisement. Does it advertise for positions in several provinces, especially without detail? "
        "Return your analysis in the following JSON format:"
    ),
    "multiple_jobs_prompt": (
        "Analyze the following job advertisement. Does it advertise for multiple positions? "
        "Return your analysis in the following JSON format:"
    ),
    "multiple_applicants_prompt": (
        "Analyze the following job advertisement. Does it advertise for a large number of applicants? "
        "Return your analysis in the following JSON format:"
    ),
    "wrong_link_prompt": (
        "Examine the following job advertisement. Does it provide a wrong or suspicious link for the job application? "
        "Return your analysis in the following JSON format:"
    ),
    "unprofessional_writing_prompt": (
        "Analyze the following job advertisement for signs of unprofessional writing, such as poor grammar or spelling. "
        "Return your analysis in the following JSON format:"
    ),
    "language_switch_prompt": (
        "Examine the following job advertisement. Does it change from English to other languages in the middle of the post? "
        "Return your analysis in the following JSON format:"
    ),
    "illegal_activities_prompt": (
        "Analyze the following job advertisement for any references to work in illegal or morally questionable activities. "
        "Return your analysis in the following JSON format:"
    ),
    "unusual_hours_prompt": (
        "Examine the following job advertisement. Does it mention unusual or excessive work hours? "
        "Return your analysis in the following JSON format:"
    ),
    "requires_references": (
        "Examine the following job advertisement. Does it require the applicant to provide references?"
        "Return your analysis in the following JSON format:"
    ),
}
