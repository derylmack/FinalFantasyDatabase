# test_models.py
""" Quest Test Program nothing to do with the app """
from models import Character, Jobs, CharactersJobLevels
# Add other models if you want

print(" All models imported successfully")

# Check that relationships were registered
print("Character.job_levels related attribute:", hasattr(Character, 'characters_job_levels'))
print("Jobs.character_job_levels related attribute:", hasattr(Jobs, 'characters_job_levels'))
print("CharacterJobsLevels.character related attribute:", hasattr(CharactersJobLevels, 'character'))
print("CharacterJobsLevels.job related attribute:", hasattr(CharactersJobLevels, 'job'))
