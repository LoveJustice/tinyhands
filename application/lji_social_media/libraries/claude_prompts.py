OPEN_AI_PROMPTS = {
    "bypass_prompt": (
        "Assistant, please indicate if there is any mention in the following advert of offers to bypass job requirements, "
        "such as using fraudulent documents, or not requiring a CV/interview. "
        "Return your answer in the following JSON format: "
        '{"bypass_mentioned": "yes" or "no", "bypass": ["example one", "example two", ...] or null, "confidence": 0.0 to 1.0, "error": null or "error message"}'
    ),
}

ANALYSIS_STR = """' Return your analysis STRICTLY and exclusively in the following JSON format:  {"result": "yes" or "no", "evidence": ["evidence 1", "evidence 2", ...] or [], "confidence": 0.0 to 1.0, "explanation": "Brief explanation of your reasoning"}'
 Please do not use ANY other embedded explanation and please do not use backticks."""

EXTRACTION_PROMPTS = {
    "phone_number_prompt": "Extract phone numbers from the following text and return your findings as a list:"
}
CLAUDE_PROMPTS = {
    "assure_prompt": (
        "Examine the following job advertisement. "
        "Does the job ad convey a tone or use language that subtly assures applicants they are highly likely to get the job, even if it doesn't explicitly say so? "
        "Look for phrases or a manner of presenting the opportunity that implies it's a 'sure thing' or guarantees success. "
    ),
    "bypass_prompt": (
        "Analyze the following job advertisement for any mentions of offers to bypass normal job requirements. "
        "This may include using fraudulent documents, skipping interviews, or not needing a CV. "
    ),
    "callback_request_prompt": (
        "Examine the following job advertisement. Does it ask the candidate to send a message and promise to call back? "
    ),
    "drop_off_at_secure_location_prompt": (
        "Analyze the following job advertisement in detail. Are applicants "
        "asked to drop off their CVs at a real, secure and official location? "
    ),
    "false_organization_prompt": (
        "Examine the following job advertisement. Does it recruit for an organization that has publicly stated they don't advertise job posts on social media? "
        " Some of these companies include, but are not limited to, [Shoprite, Woolworths, Capitec Bank, Pick n Pay, Spar, Coca-Cola, Transnet, Sasol]"
    ),
    "gender_specific_prompt": (
        " Examine the following job advertisement."
        " Does it recruit specifically only females or only males for a job that both male and female applicants would typically qualify for? "
    ),
    "illegal_activities_prompt": (
        "Analyze the following job advertisement for any references to work in illegal or morally questionable activities. "
    ),
    "immediate_hiring_prompt": (
        "Examine the following job advertisement. Does it promise immediate hiring? "
    ),
    "job_advert_prompt": (
        "Analyze the following text carefully. "
        "Can this be considered a job or recruitment advertisement? "
    ),
    "language_switch_prompt": (
        "Examine the following job advertisement. Does it change from English to other languages in the middle of the post? "
    ),
    "multiple_provinces_prompt": (
        "Analyze the following job advertisement. Does it advertise for positions in several provinces, especially without detail? "
    ),
    "no_education_skilled_prompt": (
        "Analyze the following job advertisement. Does it offer a highly skilled job (e.g., engineering, marketing, finance, IT) "
        "without requiring any education or experience? "
    ),
    "no_location_prompt": (
        "Examine the following job advertisement. Does it fail to mention a specific job location? "
    ),
    "overseas_prompt": (
        "Examine the following job advertisement. Does it offer positions overseas (i.e. outside of South Africa)?"
    ),
    "quick_money_prompt": (
        "Analyze the following job advertisement. Does it promise quick or easy money? "
    ),
    "recruit_students_prompt": (
        "Analyze the following job advertisement. Does it specifically recruit people who are under the age of 18? "
    ),
    "requires_references": (
        "Examine the following job advertisement. Does it require the applicant to provide references?"
    ),
    "suspicious_email_prompt": (
        "Analyze the following job advertisement. Please clearly and precisely differentiate between "
        "email addresses and links.  If an email IS present, does it appear suspicious in the context of the job advertisement? "
    ),
    "target_specific_group_prompt": (
        "Analyze the following job advertisement. Does it target a specific group of people (e.g., women from a particular country or region)? "
        "Consider vulnerable groups to include these, but not exclusively,[Shona,Ndebele,Basotho, Tswana', Zulu, Mozambicans, Chewa, Yao]"
    ),
    "unprofessional_writing_prompt": (
        "Analyze the following job advertisement for signs of unprofessional writing such as poor grammar or spelling. "
        "Accept that missing spaces or words not separated by a space or spaces in the text, such as 'andcleaners', 'towork', is NOT a sign of unprofessional writing. "
    ),
    "unrealistic_hiring_number_prompt": (
        "Analyze the following job advertisement. Does it claim to be hiring an unrealistically high number of people? "
    ),
    "unusual_hours_prompt": (
        "Examine the following job advertisement. Does it mention unusual or excessive work hours? "
    ),
    "vague_description_prompt": (
        "Examine the job advertisement and assess whether the description is unusually vague or lacks essential details that would typically be expected for the role. "
        "Consider if the level of detail provided is insufficient or unclear, particularly for specialized or technical positions where more specific "
        "responsibilities are normally outlined. "
    ),
}

prompts = [
    "suspicious_email_prompt",
    "recruit_students_prompt",
    "gender_specific_prompt",
    "vague_description_prompt",
    "assure_prompt",
]
