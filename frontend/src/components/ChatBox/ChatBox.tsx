import {
  Stack
} from '@mui/material'
import { useState } from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../../store/store'
import ChatFooter from './ChatBoxFooter'
import ChatHeader from './ChatBoxHeader'
import ChatHistory from './ChatBoxHistory'

export function ChatBox() {
  const [isSubmittingByClick, setIsSubmittingByClick] = useState(false)
  const state = useSelector((state: RootState) => state.chat)

  if (!state.hostname) return <></>

  return (
    <Stack border="1px solid gray">
      <ChatHeader url={state.hostname} />
      <ChatHistory
        state={state}
        setIsSubmittingByClick={setIsSubmittingByClick}
      />
      <ChatFooter state={state} isSubmittingByClick={isSubmittingByClick} />
    </Stack>
  )
}
