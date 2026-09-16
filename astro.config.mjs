import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap'; // 🟢 1. Import sitemap

export default defineConfig({
    site: 'https://doc.formmailhub.com', // 🟢 2. Cấu hình domain chuẩn để tạo sitemap
    integrations: [
        starlight({
            title: 'FormMail Hub - Docs',
            logo: {
                src: './src/assets/logo_III.svg',
            },
            favicon: '/favicon.ico',
            // 🟢 TÍCH HỢP GOOGLE ANALYTICS (GA4)
            head: [
                {
                    tag: 'script',
                    attrs: {
                        async: true,
                        src: 'https://www.googletagmanager.com/gtag/js?id=G-05MV4LHN6P',
                    },
                },
                {
                    tag: 'script',
                    content: `
                        window.dataLayer = window.dataLayer || [];
                        function gtag(){dataLayer.push(arguments);}
                        gtag('js', new Date());
                        gtag('config', 'G-05MV4LHN6P');
                    `,
                },
            ],
            social: [
                { 
                    icon: 'external', 
                    label: 'Google Workspace', 
                    href: 'https://workspace.google.com/marketplace/app/formmail_hub/409227874327' 
                },
            ],
            sidebar: [
                {
                    label: 'Guides',
                    items: [{ autogenerate: { directory: 'guides' } }],
                },
                {
                    label: 'Reference',
                    items: [{ autogenerate: { directory: 'reference' } }],
                },
                {
                    label: 'Tutorials',
                    items: [{ autogenerate: { directory: 'tutorials' } }],
                },
            ],
            customCss: ['./src/styles/global.css'],
        }),
        sitemap(), // 🟢 3. Kích hoạt tự động tạo sitemap khi build
    ],
    vite: {
        plugins: [tailwindcss()],
    },
});
