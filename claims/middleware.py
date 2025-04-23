from django.utils import timezone

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # এখানে আপনি ব্যবহারকারীর টাইমজোন নির্ধারণ করার লজিক যোগ করবেন
            # এটি ব্যবহারকারীর প্রোফাইল থেকে, সেশন থেকে, কুকি থেকে,
            # অথবা অন্য কোনো উপায়ে আসতে পারে।
            # উদাহরণস্বরূপ, যদি আপনার UserProfile মডেলে একটি timezone ফিল্ড থাকে:
            try:
                user_profile = request.user.userprofile
                if user_profile.timezone:
                    timezone.activate(user_profile.timezone)
                else:
                    timezone.deactivate()
            except AttributeError:
                timezone.deactivate()
        else:
            timezone.deactivate()
        response = self.get_response(request)
        return response