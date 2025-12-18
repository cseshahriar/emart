from django.utils import translation
from django.utils.deprecation import MiddlewareMixin


class LanguageMiddleware(MiddlewareMixin):
    """
    Custom middleware to ensure language is properly set.
    """
    def process_request(self, request):
        # Check if language is set in session
        if 'django_language' in request.session:
            language = request.session['django_language']
            translation.activate(language)
            request.LANGUAGE_CODE = language
        else:
            # Use browser language or default
            language = translation.get_language_from_request(request)
            translation.activate(language)
            request.LANGUAGE_CODE = language
