import { createRoot } from 'react-dom/client'
import { config } from '@fortawesome/fontawesome-svg-core'
import '@fortawesome/fontawesome-svg-core/styles.css'
import '@uiw/react-md-editor/markdown-editor.css'
import '@uiw/react-markdown-preview/markdown.css'
import './index.css'
import App from './App'

// We render the FontAwesome CSS ourselves (imported above), so disable the
// automatic CSS injection to avoid a flash of oversized icons.
config.autoAddCss = false

// Note: StrictMode is intentionally omitted so the SSE generation effect
// does not fire twice during development.
createRoot(document.getElementById('root')).render(<App />)
