import uuid

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, UpdateView
from .models import User
from .forms import UserCreateForm

def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


@login_required #验证是否登录
def change_password(request):
    if request.method == 'POST':
        # 传入当前登录的用户和提交的表单数据
        form = PasswordChangeForm(request.user, request.POST)

        # 检查表单数据是否有效
        if form.is_valid():
            # 保存新密码
            form.save()
            # 保证修改密码后用户仍然保持登录状态
            update_session_auth_hash(request, form.user)

            # 重定向或返回成功消息
            return redirect('user:change_password_success')  # 假设有一个密码修改成功的页面
        else:
            return redirect('user:change_password_fail')
    else:
        form = PasswordChangeForm(request.user)

    # 渲染密码更改表单
    return render(request, 'change_password.html', {'form': form})


class SignUpView(CreateView):
    form_class = UserCreateForm
    template_name = 'signup.html'
    success_url = reverse_lazy('user:signup_success')

    def form_valid(self, form):

        # 在保存用户之前为 user_id 字段生成一个随机的 UUID
        user = form.save(commit=False)  # 先创建用户对象，但不保存到数据库
        user.user_id = uuid.uuid4()  # 生成并赋值一个新的 UUID
        user.save()  # 保存用户
        self.object = user  # 将保存的对象赋值给 self.object
        return super().form_valid(form)  # 调用父类的 form_valid 方法


class SignUpSuccessView(TemplateView):
    template_name = 'signup_success.html'


class UpdateUser(LoginRequiredMixin, UpdateView):
    template_name = 'update_user.html'
    model = User
    fields = ['name', 'email']

    def get_success_url(self):
        user_id = self.request.POST.get('user_id')
        # 根据条件动态生成重定向 URL
        return reverse('article:my_article', kwargs={'user': user_id})

class ChangePasswordFail(TemplateView):
    template_name = 'change_password_fail.html'

class ChangePasswordSuccess(TemplateView):
    template_name = 'change_password_success.html'

