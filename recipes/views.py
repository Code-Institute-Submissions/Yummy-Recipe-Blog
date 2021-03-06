from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .models import LikedRecipe, Recipe, Category
from .forms import RecipeCreationForm
from accounts.models import Account

# Create your views here.


@login_required(login_url='/')
def create_recipe(request) -> render:
    """
    Creates the create recipe view.

    Args:
        request (HttpRequest): A HttpRequest class object.

    Returns:
        render: A HttpResponse whose content is filled by the provided template and context.
    """
    if request.method == 'POST':
        form = RecipeCreationForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            servings = form.cleaned_data.get('servings')
            prep_time = form.cleaned_data.get('prep_time')
            cook_time = form.cleaned_data.get('cook_time')
            total_time = prep_time + cook_time
            form_categories = form.cleaned_data['categories'].split(',')
            image = form.cleaned_data.get('image')
            ingredients = form.cleaned_data.get('ingredients')
            steps = form.cleaned_data.get('steps')
            author = Account.objects.get(username=request.user.username)
            for category in form_categories:
                if category not in Category.objects.all():
                    Category.objects.create(name=category)

            categories = Category.objects.filter(name__in=form_categories)

            recipe = Recipe.objects.create(name=name, servings=servings, prep_time=prep_time, cook_time=cook_time,
                                           total_time=total_time, image=image, ingredients=ingredients, steps=steps, author=author)

            recipe.category.set(categories)

            return redirect('home')

    user = Account.objects.get(username=request.user.username)
    form = RecipeCreationForm()
    context = {
        'title': 'Create Recipe',
        'form': form,
        'user': user
    }

    return render(request, 'recipes/create_recipe.html', context)


@login_required(login_url='/')
def edit_recipe(request, recipe_id):
    user = Account.objects.get(username=request.user.username)
    recipe = Recipe.objects.get(id=recipe_id)
    form = RecipeCreationForm(instance=recipe)
    form.is_multipart()
    context = {
        'title': 'Recipe',
        'user': user,
        'form': form,
    }
    
    if request.method == 'POST':
        form = RecipeCreationForm(request.POST, request.FILES, instance=recipe)
        form.is_multipart()
        if form.is_valid():
            form.save()
            return redirect('personal_recipes')
        
    return render(request, 'recipes/edit_recipes.html', context)


@login_required(login_url='/')
def like_recipe(request, recipe_id) -> redirect:
    """
    Likes the current recipe.

    Args:
        request (HttpRequest): A HttpRequest class object.
        recipe_id (int): The Id from the current recipe.

    Returns:
        redirect: Rediects the user to the provided url.
    """
    recipe = Recipe.objects.get(id=recipe_id)
    recipe.likes += 1
    user = Account.objects.get(username=request.user.username)
    LikedRecipe.objects.create(recipe=recipe, liked_by=user)
    return redirect('home')


@login_required(login_url='/')
def recipe_page(request, recipe_id) -> render:
    """
    Renders the recipe page.

    Args:
        request (HttpRequest): A HttpRequest class object.
        recipe_id (int): The Id from the current recipe.

    Returns:
        render: An HttpResponse whose content is filled by the provided template and context.
    """
    recipe = Recipe.objects.get(id=recipe_id)
    user = Account.objects.get(username=request.user.username)
    context = {
        'title': recipe.name,
        'user': user,
        'recipe': recipe
    }
    return render(request, 'recipes/recipe_page.html', context)
