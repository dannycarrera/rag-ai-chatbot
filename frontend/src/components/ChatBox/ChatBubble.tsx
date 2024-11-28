import Grid from '@mui/material/Grid2'
import React from 'react'
import { ChatText } from './ChatText'
import { MessageType } from './MessageType'

export function ChatBubble({
  messageType,
  children,
}: {
  messageType: MessageType
  children: React.ReactNode
}) {
  return (
    <Grid>
      <ChatText messagetype={messageType}>{children}</ChatText>
    </Grid>
  )
}
