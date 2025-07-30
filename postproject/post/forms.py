from django import forms
from .models import Post

# show all index
class IndexPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'video']

# create new post
class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'video']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter title here'}),
            'content': forms.Textarea(attrs={'placeholder': 'Write your content here...'}),
        }

    def __init__(self,name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Explicitly mark required/optional
        self.fields['title'].required = True
        self.fields['content'].required = True
        self.fields['image'].required = False
        self.fields['video'].required = False


