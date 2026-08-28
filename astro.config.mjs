import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    integrations: [
        starlight({
            title: 'FormMail Hub - Documentation',
            logo: {
                src: './src/assets/logo_3.svg',
            },
            favicon: '/favicon.ico',
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
                    // Đã đưa autogenerate vào trong items
                    items: [{ autogenerate: { directory: 'guides' } }],
                },
                {
                    label: 'Reference',
                    // Đã đưa autogenerate vào trong items
                    items: [{ autogenerate: { directory: 'reference' } }],
                },
                {
                    label: 'Tutorials',
                    // Đã đưa autogenerate vào trong items
                    items: [{ autogenerate: { directory: 'tutorials' } }],
                },
            ],
            customCss: ['./src/styles/global.css'],
        }),
    ],
    vite: {
        plugins: [tailwindcss()],
    },
});
