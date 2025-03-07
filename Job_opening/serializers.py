from rest_framework import serializers
from .models import Company, JobOpening, FormField, ApplicantResponse, ArchivedJobOpening
import re
import json


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ["id", "question", "field_type", "is_required", "options"]

class JobOpeningSerializer(serializers.ModelSerializer):
    form_fields = FormFieldSerializer(many=True)

    class Meta:
        model = JobOpening
        fields = ["id", "title", "description", "form_url", "created_at","deadline", "form_fields"]

    def create(self, validated_data):
        form_fields_data = validated_data.pop("form_fields")
        job_opening = JobOpening.objects.create(**validated_data)
        for field_data in form_fields_data:
            FormField.objects.create(job_opening=job_opening, **field_data)
        # Generate form_url (e.g., using UUID or slug)
        job_opening.form_url = f"/apply/{job_opening.id}/"
        job_opening.save()
        return job_opening
    
    def update(self, instance, validated_data):
        # Update JobOpening fields
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.deadline = validated_data.get("deadline", instance.deadline)
        instance.save()

        # Handle form_fields updates
        if "form_fields" in validated_data:
            form_fields_data = validated_data.pop("form_fields")
            existing_fields = {field.id: field for field in instance.form_fields.all()}
            updated_field_ids = {field["id"] for field in form_fields_data if "id" in field}

            # Delete form fields not in the updated data
            for field_id, field in existing_fields.items():
                if field_id not in updated_field_ids:
                    field.delete()

            # Update or create form fields
            for field_data in form_fields_data:
                field_id = field_data.get("id")
                if field_id and field_id in existing_fields:
                    # Update existing field
                    field = existing_fields[field_id]
                    field.question = field_data.get("question", field.question)
                    field.field_type = field_data.get("field_type", field.field_type)
                    field.is_required = field_data.get("is_required", field.is_required)
                    field.options = field_data.get("options", field.options)
                    field.save()
                else:
                    # Create new field
                    FormField.objects.create(job_opening=instance, **field_data)

        return instance

class ApplicantResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantResponse
        fields = ["id", "job_opening", "email_address", "name", "gender", "country", "phone_number", "responses", "cv", "submitted_at"]

    def validate_responses(self, value):
        # Handle case where value is a string (from form-data)
        if isinstance(value, str):
            try:
                value = json.loads(value)  # Parse JSON string to dict
            except json.JSONDecodeError:
                raise serializers.ValidationError("Responses must be a valid JSON object.")

        # Ensure value is a dict
        if not isinstance(value, dict):
            raise serializers.ValidationError("Responses must be a dictionary.")

        response_keys = set(value.keys())
        job_opening = self.initial_data.get("job_opening")
        try:
            job = JobOpening.objects.get(id=job_opening)
            form_fields = job.form_fields.all()
            required_keys = {field.question for field in form_fields if field.is_required}
            all_keys = {field.question for field in form_fields}

            missing_keys = required_keys - response_keys
            extra_keys = response_keys - all_keys

            if missing_keys:
                raise serializers.ValidationError(f"Missing required fields: {', '.join(missing_keys)}")
            if extra_keys:
                raise serializers.ValidationError(f"Unexpected fields: {', '.join(extra_keys)}")

            # Validate response types match form field types
            for field in form_fields:
                question = field.question
                if question in value:
                    response = value[question]
                    if field.field_type == "number":
                        if not response.isdigit():
                            raise serializers.ValidationError(f"'{question}' must be a number.")
                    elif field.field_type == "text":
                        if not isinstance(response, str):
                            raise serializers.ValidationError(f"'{question}' must be a string.")
                    elif field.field_type == "choice":
                        if response not in field.options:
                            raise serializers.ValidationError(f"'{question}' must be one of: {', '.join(field.options)}.")
        except JobOpening.DoesNotExist:
            raise serializers.ValidationError("Invalid job opening ID.")
        return value
    
    def validate_gender(self, value):
        """Ensure gender is either 'male' or 'female'."""
        valid_genders = ["male", "female"]
        if value not in valid_genders:
            raise serializers.ValidationError(f"Gender must be one of: {', '.join(valid_genders)}.")
        return value
    
    def _is_valid_email(self, email):
        """Simple email validation using regex."""
        if not isinstance(email, str):
            return False
        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        return bool(email_pattern.match(email))
    
    
class ArchivedJobOpeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivedJobOpening
        fields = ["id", "title", "description", "form_url", "created_at", "deadline", "archived_at"]