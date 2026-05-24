// 🦞 龙虾兵团 · 交互脚本
document.addEventListener('DOMContentLoaded', function() {
    // 移动端菜单
    document.getElementById('menuToggle').addEventListener('click', function() {
        document.getElementById('navLinks').classList.toggle('active');
    });

    // 点击导航链接关闭菜单
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            document.getElementById('navLinks').classList.remove('active');
        });
    });

    // 注册弹窗
    window.showRegister = function() {
        document.getElementById('registerModal').classList.add('active');
        document.body.style.overflow = 'hidden';
    };
    window.hideRegister = function() {
        document.getElementById('registerModal').classList.remove('active');
        document.body.style.overflow = '';
    };

    // 购买弹窗
    window.showBuy = function(plan, price) {
        document.getElementById('buyTitle').textContent = '💎 ' + plan;
        document.getElementById('payAmount').textContent = '¥' + price + '（约$' + Math.round(price/7) + '）';
        document.getElementById('buyModal').classList.add('active');
        document.body.style.overflow = 'hidden';
    };
    window.hideBuy = function() {
        document.getElementById('buyModal').classList.remove('active');
        document.body.style.overflow = '';
    };

    // 点击弹窗背景关闭
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    // 下载按钮中的注册弹窗
    document.querySelectorAll('.download-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            showRegister();
        });
    });

    // 注册表单提交（用Formspree，免费）
    document.getElementById('registerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const btn = this.querySelector('button[type="submit"]');
        btn.textContent = '⏳ 提交中...';
        btn.disabled = true;

        // 模拟提交成功（后续接Formspree或Supabase）
        setTimeout(() => {
            btn.textContent = '✅ 注册成功！下载链接已发送';
            setTimeout(() => {
                hideRegister();
                // 直接展示免费资源链接
                alert('📧 下载链接已发送到你的邮箱！\n\n也可直接下载：\n📦 口播模板: https://github.com/...\n📘 交易战法: https://...\n🌐 建站模板: https://...');
            }, 1500);
        }, 1500);
    });

    // 需求表单提交
    document.querySelector('.contact-form').addEventListener('submit', function(e) {
        e.preventDefault();
        const btn = this.querySelector('button');
        btn.textContent = '✅ 已提交，我们会尽快联系你！';
        btn.style.background = '#51cf66';
        setTimeout(() => {
            btn.textContent = '📨 提交需求';
            btn.style.background = '';
            this.reset();
        }, 3000);
    });
});
