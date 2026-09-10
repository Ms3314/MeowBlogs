import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Generator from './pages/Generator'
import History from './pages/History'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-full flex-col">
        <Navbar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/generate" element={<Generator />} />
            <Route path="/history" element={<History />} />
            <Route path="*" element={<Landing />} />
          </Routes>
        </main>
        <footer className="border-t border-orange-100 py-6 text-center text-xs text-slate-400">
          MeowBlogs
        </footer>
      </div>
    </BrowserRouter>
  )
}
