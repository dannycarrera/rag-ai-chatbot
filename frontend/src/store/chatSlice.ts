import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

export type ChatMessageBase = {
  content: string
  mc_options?: string[]
}
export type ChatMessage = {
  from: 'ai' | 'user'
  pendingSend?: true
} & ChatMessageBase

export type StartChatPayloadType = {
  passphrase: string
  hostname: string
  threadId: string
  message: ChatMessage
}

export interface ChatState {
  passphrase: string | null
  hostname: string | null
  threadId: string | null
  messages: ChatMessage[]
}


export const initialChatState: ChatState = {
  passphrase: null,
  hostname: null,
  threadId: null,
  messages: [],
}

export const chatSlice = createSlice({
  name: 'chat',
  initialState: initialChatState,
  reducers: {
    startChat: (state, action: PayloadAction<StartChatPayloadType>) => {
      state.passphrase = action.payload.passphrase
      state.hostname = action.payload.hostname
      state.threadId = action.payload.threadId
      state.messages.push(action.payload.message)
    },
    addMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.messages.push(action.payload)
    },
    resetChat: (state) => {
      state.hostname = null
      state.threadId = null
      state.messages = []
    },
  },
})

export const { startChat, addMessage, resetChat } = chatSlice.actions

export default chatSlice.reducer
