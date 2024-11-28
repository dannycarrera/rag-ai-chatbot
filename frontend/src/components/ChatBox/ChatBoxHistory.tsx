import { Box, Grid2 } from '@mui/material'
import { useEffect, useRef } from 'react'
import { ChatState } from '../../store/chatSlice'
import { AIMessage } from './AIMessage'
import { UserMessage } from './UserMessage'
export default function ChatHistory({
  state,
  setIsSubmittingByClick,
}: {
  state: ChatState
  setIsSubmittingByClick: React.Dispatch<React.SetStateAction<boolean>>
}) {
  const scrollRef = useRef<HTMLDivElement | null>(null)
  const msgLengthRef = useRef<number>(state.messages.length)
  
  // Initial scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth', // Optional: Adds smooth scrolling animation
      })
    }
  }, [scrollRef])
  // Add message scroll
  useEffect(() => {
    if (scrollRef.current && msgLengthRef.current < state.messages.length) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth', // Optional: Adds smooth scrolling animation
      })
      msgLengthRef.current = state.messages.length
    }
  }, [scrollRef, msgLengthRef, state])
  return (
    <Box
      ref={scrollRef}
      sx={{
        backgroundColor: 'lightgrey',
        maxWidth: '800px',
        maxHeight: '400px',
        padding: 1,
        overflowY: 'scroll',
      }}
    >
      <Grid2 container spacing={2}>
        {state.messages.map((m, i) =>
          m.from === 'ai' ? (
            <AIMessage
              key={i}
              state={state}
              message={m}
              setIsSubmittingByClick={setIsSubmittingByClick}
            />
          ) : (
            <UserMessage key={i} message={m} />
          )
        )}
      </Grid2>
    </Box>
  )
}
