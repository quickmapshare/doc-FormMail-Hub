import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    integrations: [
        starlight({
            title: 'Doc FormMail Hub',
            favicon: '/favicon.ico', // ← Thêm dòng này vào đây
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
                    items: [
                        { label: 'FormMail Hub Guide', slug: 'guides/formmailhub' },
                    ],
                },
                {
                    label: 'Reference',
                    items: [{ autogenerate: { directory: 'reference' } }],
                },
            ],
            customCss: ['./src/styles/global.css'],
        }),
    ],
    vite: {
        plugins: [tailwindcss()],
    },
});