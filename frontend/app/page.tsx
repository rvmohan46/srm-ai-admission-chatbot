'use client'

import { FormEvent, useState } from 'react'
import {
  ArrowUpRight,
  Bot,
  Check,
  ChevronRight,
  CircleHelp,
  ExternalLink,
  GraduationCap,
  House,
  Menu,
  MessageCircle,
  Phone,
  Plus,
  Send,
  ShieldCheck,
  Sparkles,
  WalletCards,
  X,
} from 'lucide-react'

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001'

const faqs = [
  { icon: GraduationCap, title: 'B.Tech Eligibility & Cutoffs', prompt: 'What are the B.Tech eligibility requirements and cutoffs?' },
  { icon: CircleHelp, title: 'SRMJEEE Deadlines & Exam Pattern', prompt: 'What are the SRMJEEE deadlines and exam pattern?' },
  { icon: WalletCards, title: 'Tuition Fees & Scholarships', prompt: 'Tell me about B.Tech tuition fees and scholarships.' },
  { icon: House, title: 'Hostel Amenities & Allocations', prompt: 'What hostel amenities and allocation options are available?' },
]

const mockReply = "For B.Tech CSE at Kattankulathur, eligibility typically includes a pass in 10+2 with Physics and Mathematics as compulsory subjects, along with one of Chemistry, Biotechnology, Biology, or a technical vocational subject. Admissions are based on SRMJEEE performance. For the latest cutoffs and official fee details, please check the current admission notice or contact the Directorate of Admissions."

export default function Page() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [activeFilter, setActiveFilter] = useState('All')
  const [query, setQuery] = useState('')
  const [sessionId] = useState(() => 'session_' + Math.random().toString(36).substring(2, 9))
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Welcome to SRM Institute of Science & Technology. I can help with courses, eligibility, SRMJEEE, fees, scholarships, and hostel information for 2026–27 admissions.' },
  ])

  const askQuestion = async (question: string) => {
    const trimmed = question.trim()
    if (!trimmed) return
    setMessages((current) => [...current, { role: 'user', text: trimmed }])
    setQuery('')
    try {
      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: trimmed }),
      })
      if (!response.ok) throw new Error('Request failed')
      const data = await response.json()
      setMessages((current) => [...current, { role: 'bot', text: data.bot_response || data.reply || mockReply }])
    } catch {
      setTimeout(() => setMessages((current) => [...current, { role: 'bot', text: 'Connecting to AI Admission Assistant...' }]), 450)
    }
  }

  const submitQuery = (event?: FormEvent) => {
    event?.preventDefault()
    void askQuestion(query)
  }

  return (
    <main className="min-h-screen bg-[#F4F6F9] text-[#1F2937]">
      <header className="bg-[#002147] text-white">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-5 px-5 py-4 lg:px-8">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-[#E5A823]/60 bg-white/10 text-[#E5A823]" aria-label="SRM emblem">
              <span className="text-lg font-black tracking-[-0.1em]">SRM</span>
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-bold tracking-[0.08em]">SRM INSTITUTE OF SCIENCE & TECHNOLOGY</p>
              <p className="truncate text-[11px] text-white/65">Directorate of Admissions <span className="mx-1 text-[#E5A823]">|</span> 2026–27</p>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full bg-[#0B3C5D] px-4 py-2 text-xs font-semibold md:flex">
            <span className="size-2 animate-pulse rounded-full bg-[#E5A823]" /> SRMJEEE Phase 1 Admissions Open
          </div>
          <div className="hidden items-center gap-5 lg:flex">
            <a href="tel:04427455510" className="flex items-center gap-2 text-xs font-medium text-white/80 hover:text-white"><Phone size={14} /> 044-27455510</a>
            <a href="https://srmist.edu.in" target="_blank" rel="noreferrer" className="flex items-center gap-1 text-xs text-white/80 hover:text-white">srmist.edu.in <ExternalLink size={13} /></a>
            <a href="https://applications.srmist.edu.in" target="_blank" rel="noreferrer" className="rounded-lg bg-[#E5A823] px-4 py-2.5 text-xs font-bold text-[#002147] shadow-lg shadow-black/10 transition hover:bg-[#f4bd3e]">Apply Now</a>
          </div>
          <button className="rounded-lg p-2 lg:hidden" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle menu">{menuOpen ? <X size={20} /> : <Menu size={20} />}</button>
        </div>
        {menuOpen && <div className="border-t border-white/10 px-5 py-4 lg:hidden"><div className="flex flex-wrap gap-3 text-xs"><a href="tel:04427455510">044-27455510</a><a href="https://srmist.edu.in">srmist.edu.in</a><a className="rounded-md bg-[#E5A823] px-3 py-2 font-bold text-[#002147]" href="https://applications.srmist.edu.in">Apply Now</a></div></div>}
      </header>

      <div className="mx-auto grid max-w-[1500px] gap-6 px-5 py-6 lg:grid-cols-[265px_minmax(0,1fr)] lg:px-8">
        <aside className="hidden flex-col gap-5 lg:flex">
          <button onClick={() => setMessages([{ role: 'bot', text: 'New admission query started. How can I help you today?' }])} className="flex items-center justify-center gap-2 rounded-xl bg-[#E5A823] px-4 py-3 text-sm font-bold text-[#002147] shadow-lg shadow-[#002147]/10 transition hover:-translate-y-0.5 hover:bg-[#f4bd3e]"><Plus size={17} /> New Admission Query</button>
          <section className="rounded-2xl border border-[#E1E8ED] bg-white p-4 shadow-[0_10px_25px_rgba(0,33,71,0.08)]">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.14em] text-[#6B7280]">Browse topics</p>
            <div className="flex flex-wrap gap-2">{['All', 'Eligibility', 'Fees', 'SRMJEEE', 'Hostel'].map((filter) => <button key={filter} onClick={() => setActiveFilter(filter)} className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${activeFilter === filter ? 'bg-[#0B3C5D] text-white' : 'bg-[#F4F6F9] text-[#526070] hover:bg-[#e9eef3]'}`}>{filter}</button>)}</div>
          </section>
          <section className="rounded-2xl border-l-4 border-[#E5A823] bg-white p-4 shadow-[0_10px_25px_rgba(0,33,71,0.08)]">
            <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.12em] text-[#6B7280]">Current session</p>
            <p className="text-sm font-bold leading-5 text-[#002147]">Admission Queries & Verification</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-[#607080]"><span className="size-2 rounded-full bg-emerald-500" /> Active now</div>
          </section>
          <section className="mt-auto rounded-2xl bg-[#002147] p-5 text-white shadow-xl shadow-[#002147]/15"><p className="text-[11px] font-bold uppercase tracking-[0.13em] text-[#E5A823]">Target campus</p><p className="mt-2 text-sm font-semibold leading-5">Kattankulathur (Main Campus), Chennai</p><button className="mt-4 flex items-center gap-1 text-xs font-semibold text-white/70 hover:text-white">Campus details <ChevronRight size={14} /></button></section>
        </aside>

        <section className="min-w-0">
          <div className="mb-5 flex items-start justify-between gap-4 rounded-2xl border border-[#E1E8ED] bg-white p-5 shadow-[0_10px_25px_rgba(0,33,71,0.08)] sm:p-6">
            <div className="flex gap-4"><div className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-[#002147] text-[#E5A823]"><Bot size={25} /></div><div><div className="mb-1 flex flex-wrap items-center gap-2"><h1 className="font-bold tracking-[-0.02em] text-[#002147] sm:text-lg">SRM AI Admission Support Assistant</h1><span className="flex items-center gap-1 rounded-full bg-[#eaf5ef] px-2 py-1 text-[10px] font-bold text-[#23744b]"><ShieldCheck size={12} /> Official Support</span></div><p className="text-xs leading-5 text-[#687789] sm:text-sm">Official information on courses, fees, eligibility, and entrance examinations.</p></div></div><Sparkles className="hidden shrink-0 text-[#E5A823] sm:block" size={20} />
          </div>

          <div className="mb-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{faqs.map(({ icon: Icon, title, prompt }) => <button key={title} onClick={() => void askQuestion(prompt)} className="group flex min-h-[88px] items-center gap-3 rounded-xl border border-[#E1E8ED] bg-white p-4 text-left shadow-[0_7px_18px_rgba(0,33,71,0.05)] transition hover:-translate-y-0.5 hover:border-[#E5A823] hover:shadow-[0_10px_22px_rgba(229,168,35,0.13)]"><span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-[#fff6df] text-[#b37b00] transition group-hover:bg-[#E5A823] group-hover:text-[#002147]"><Icon size={18} /></span><span className="text-xs font-bold leading-4 text-[#243b53]">{title}</span><ArrowUpRight size={15} className="ml-auto shrink-0 text-[#9aa8b5] transition group-hover:text-[#002147]" /></button>)}</div>

          <div className="rounded-2xl border border-[#E1E8ED] bg-white shadow-[0_10px_25px_rgba(0,33,71,0.08)]">
            <div className="flex items-center justify-between border-b border-[#edf0f3] px-5 py-4"><div><p className="text-sm font-bold text-[#002147]">Admission conversation</p><p className="text-[11px] text-[#7A8794]">Your queries are answered using official admission guidance.</p></div><span className="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600"><span className="size-1.5 rounded-full bg-emerald-500" /> Online</span></div>
            <div className="max-h-[390px] min-h-[280px] space-y-5 overflow-y-auto bg-[#fbfcfd] p-5 sm:p-6">{messages.map((message, index) => message.role === 'user' ? <div key={index} className="flex justify-end"><div className="max-w-[82%] rounded-2xl rounded-br-md bg-[#002147] px-4 py-3 text-sm leading-6 text-white shadow-sm">{message.text}</div></div> : <div key={index} className="flex items-start gap-3"><div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-[#002147] text-[#E5A823]"><Bot size={17} /></div><div className="max-w-[88%]"><div className="mb-1.5 flex items-center gap-2"><span className="text-[11px] font-bold text-[#002147]">SRM Official Support</span><span className="flex size-4 items-center justify-center rounded-full bg-[#eaf5ef] text-[#23804f]"><Check size={10} strokeWidth={3} /></span></div><div className="rounded-2xl rounded-tl-md border border-[#E1E8ED] bg-white px-4 py-3 text-sm leading-6 text-[#3f4e5d] shadow-sm">{message.text}</div></div></div>)}</div>
            <form onSubmit={submitQuery} className="border-t border-[#edf0f3] bg-white p-4 sm:p-5"><div className="flex items-center gap-3 rounded-full border border-[#d8e0e7] bg-[#F4F6F9] p-1.5 pl-4 transition focus-within:border-[#E5A823] focus-within:ring-2 focus-within:ring-[#E5A823]/20"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Type your query (e.g., What is the tuition fee for B.Tech CSE at Kattankulathur?)..." className="min-w-0 flex-1 bg-transparent py-2 text-xs text-[#1F2937] outline-none placeholder:text-[#8b98a5] sm:text-sm" aria-label="Admission query" /><button type="submit" className="flex size-10 shrink-0 items-center justify-center rounded-full bg-[#002147] text-[#E5A823] transition hover:bg-[#0B3C5D]" aria-label="Send query"><Send size={17} /></button></div><p className="mt-2 px-2 text-[10px] text-[#8b98a5]">For official confirmation, always refer to the latest notices at srmist.edu.in.</p></form>
          </div>
        </section>
      </div>
      <footer className="mx-auto flex max-w-[1500px] items-center justify-between px-5 pb-6 text-[10px] text-[#82909d] lg:px-8"><span>SRM Institute of Science & Technology · Directorate of Admissions</span><span className="hidden items-center gap-1 sm:flex"><MessageCircle size={12} /> Support portal</span></footer>
    </main>
  )
}
