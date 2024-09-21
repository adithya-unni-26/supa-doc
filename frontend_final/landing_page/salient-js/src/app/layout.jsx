import { Inter, Lexend } from 'next/font/google'
import clsx from 'clsx'

import '@/styles/tailwind.css'

export const metadata = {
  title: {
    template: '%s - Supa-Doc',
    default: 'Supa-Doc - AI-Powered Documentation Chatbots',
  },
  description:
    'Create, manage, and embed AI-powered chatbots that interact with your documentation. Enhance your user experience with intelligent, context-aware assistance.',
}

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const lexend = Lexend({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-lexend',
})

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={clsx(
        'h-full scroll-smooth bg-white antialiased',
        inter.variable,
        lexend.variable,
      )}
    >
      <body className="flex h-full flex-col">
        <main className="flex-grow">{children}</main>
      </body>
    </html>
  )
}
