import './App.css'
import { Box, Typography } from '@mui/material'
import { AppForm, ChatBox } from './components'
import { useSelector } from 'react-redux'
import { RootState } from './store/store'

function App() {
  const state = useSelector((state: RootState) => state.chat)

  return (
    <div className="App">
      <header className="App-header">
        <Typography variant="h3" color="primary" marginBottom={10}>
          RAG AI Chatbot
        </Typography>
        {!state.hostname ? <AppForm /> : <ChatBox />}
        <Box paddingBottom={10}></Box>
      </header>
    </div>
  )
}

export default App
