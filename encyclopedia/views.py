from django.shortcuts import render, redirect
from django.urls import reverse
from markdown2 import Markdown
from django import forms
from django.contrib import messages
import random
from . import util

class SearchForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={
        "class" : "search",
        "placeholder" : "Search Encyclopedia" 
    }))

class CreateForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={
        "placeholder" : "Title"
    }))
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        "placeholder" : "Content"
    }))

class EditForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea(attrs={
        "placeholder" : "Enter page content",
    }))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form" : SearchForm()
    })

def entry(request, title):
    entry_md = util.get_entry(title)

    if entry_md != None:
        entry_html = Markdown().convert(entry_md)
        return render(request, "encyclopedia/entry.html", {
            "title" : title,
            "entry" : entry_html,
            "form" : SearchForm()
        })
    
    else:
        return render(request, "encyclopedia/error.html", {
            "title" : title,
            "form" : SearchForm()
        })
    
def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            entry_md = util.get_entry(title)

            if entry_md:
                return redirect(reverse('entry', args=[title]))
            
            else:
                entries = util.list_entries()
                entriess = []
                for entry in entries:
                    if title in entry:
                        entriess.append(entry)
                return render(request, "encyclopedia/search.html", { 
                    "title" : title,
                    "entries": entriess,
                    "form" : SearchForm()
                })

    return redirect(reverse("index"))

def create(request):
    if request.method == "GET":
       return render(request, "encyclopedia/create.html", {
          "form" : SearchForm(),
          "create_form" : CreateForm()
       })

    elif request.method == "POST":
        form = CreateForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
        else:
            messages.error(request, "Entry form is not valid")
            return render(request, "encyclopedia/create.html", {
                "form" : SearchForm(),
                "create_form" : CreateForm()
            })

        if util.get_entry(title):
            messages.error(request, "Title already exists, Please change the title")
            return render(request, "encyclopedia/create.html", {
                "form" : SearchForm(),
                "create_form" : CreateForm()
            })
        else:
            util.save_entry(title, content)
            messages.success(request, f"Page '{title}' successfully created")
            return redirect(reverse('entry', args=[title]))
        
def edit(request, title):
    if request.method == "GET":
        content = util.get_entry(title)

        if content == None:
            messages.error(request, "The entered page does not exist")

        return render(request, "encyclopedia/edit.html", {
            "title" : title,
            "form" : SearchForm(),
            "edit_form" : EditForm(initial={"content":content})
        })
    
    elif request.method == "POST":
        form = EditForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            messages.success(request, "Page successfully edited")
            return redirect(reverse('entry', args=[title]))
        
        else:
            messages.error(request, "Editing form is invalid")
            return render(request, "encyclopedia/edit.html", {
                "title" : title,
                "form" : SearchForm(),
                "edit_form" : EditForm(initial={"content":content})
            })

def random_page(request):
    titles = util.list_entries()
    title = random.choice(titles)

    return redirect(reverse(entry, args=[title]))