"""
Sample output: what a complete process-document response looks like.
This is for documentation / testing reference only.
"""
SAMPLE_PROCESS_DOCUMENT_RESPONSE = {
  "success": True,
  "document_name": "privacy_policy.pdf",
  "total_pages": 12,
  "total_clauses": 10,
  "processing_status": "completed",
  "clauses": [
    {
      "clause_number": 1,
      "clause_title": "Third Party Data Sharing",
      "original_text": "The company may share personal information with third-party service providers.",
      "category": "Data Sharing with Third Parties",
      "category_id": 2,
      "classification_confidence": 0.87,
      "classification_method": "hybrid_rule",
      "secondary_categories": [],
      "severity_prior": 0.80,
      "embedding": [],
      "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
      "embedding_dimension": 0,
      "simple_explanation": (
        "The company can share your personal information with external organizations "
        "that help it run its services.\n"
        "⚠️ This is an AI-generated explanation for informational purposes, not legal advice."
      ),
      "summarization_model": "gpt-4o-mini",
      "summarization_provider": "openai",
      "is_mock_summary": False,
      "processing_status": "completed",
      "errors": []
    }
  ],
  "metrics": {
    "extraction_time_s": 0.4,
    "cleaning_time_s": 0.05,
    "segmentation_time_s": 0.2,
    "classification_time_s": 0.3,
    "embedding_time_s": 1.5,
    "summarization_time_s": 3.2,
    "total_time_s": 5.65
  },
  "error_message": ""
}
