from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group
from django import forms

User = get_user_model()
POST_ID = '1'
POST_TEXT = 'Тестовый пост'
USER_NAME = 'TestUser'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
GROUP_DISCRIPTION = 'Тестовое описание'

TEMLATES_PAGES = {
    reverse('posts:index'): 'posts/index.html',
    (reverse('posts:group', kwargs={'slug': GROUP_SLUG})):
        'posts/group_list.html',
    (reverse('posts:profile', kwargs={'username': USER_NAME})):
        'posts/profile.html',
}



class PostPagesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DISCRIPTION
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=Group.objects.get(title=GROUP_TITLE),
            author=cls.user
        )


    def setUp(self):
        self.autorized_client = Client()
        self.user = User.objects.get(username=USER_NAME)
        self.autorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group', kwargs={'slug': GROUP_SLUG})):
                'posts/group_list.html',
            (reverse('posts:profile', kwargs={'username': USER_NAME})):
                'posts/profile.html',
            (reverse('posts:post_detail', kwargs={'post_id': POST_ID})):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (reverse('posts:edit', kwargs={'post_id': POST_ID})):
                'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.autorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_correct_context(self):
        response = self.autorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_list_page_show_correct_context(self):
        first_obj = 0
        for reverse_name, template in TEMLATES_PAGES.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.autorized_client.get(reverse_name)
                first_object = response.context['page_obj'][first_obj]
                self.assertEqual(first_object.text,
                                 POST_TEXT,
                                 f'page_obg неверно передается в {template}')
                self.assertEqual(first_object.group.title,
                                 GROUP_TITLE,
                                 f'page_obg неверно передается в {template}')

    def test_posts_correct_context_post_detail(self):
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': POST_ID})
        )
        first_object = response.context['post']
        self.assertEqual(first_object.text,
                         POST_TEXT,
                         f'post неверно передается в {response}')
        self.assertEqual(first_object.group.title,
                         GROUP_TITLE,
                         f'post неверно передается в {response}')

    def test_posts_correct_context_post_edit(self):
        response = self.autorized_client.get(
            reverse('posts:edit', kwargs={'post_id': POST_ID}))
        first_object = response.context['post']
        self.assertEqual(first_object.text,
                         POST_TEXT,
                         f'post неверно передается в {response}')
        self.assertEqual(first_object.group.title,
                         GROUP_TITLE,
                         f'post неверно передается в {response}')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        COUNT_POST = 13
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER_NAME)

        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DISCRIPTION
        )

        for i in range(COUNT_POST):
            cls.post = Post.objects.create(
                text='Тестовый пост',
                group=Group.objects.get(title=GROUP_TITLE),
                author=cls.user
            )

    def setUp(self):
        self.autorized_client = Client()
        self.user = User.objects.get(username=USER_NAME)
        self.autorized_client.force_login(self.user)

    def test_first_page_contains_paginator(self):
        ten_pages = 10
        three_pages = 3
        for reverse_name, template in TEMLATES_PAGES.items():
            with self.subTest(reverse_name=reverse_name):
                response_one = self.client.get(reverse_name)
                response_two = self.client.get(
                    f'{reverse_name}?page=2'
                )
                self.assertEqual(
                    len(response_one.context['page_obj']),
                    ten_pages,
                    f'Paginator страницы - 1, '
                    f'{reverse_name} работает не правильно'
                )
                self.assertEqual(
                    len(response_two.context['page_obj']),
                    three_pages,
                    f'Paginator страницы - 2, '
                    f'{reverse_name} работает не правильно'
                )

