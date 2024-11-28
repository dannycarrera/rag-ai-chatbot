import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { ChatMessageBase } from './chatSlice'

export type StartChatQueryType = {
    url: string
    passphrase: string
  }
export type StartChatReturnType = {thread_id: string, message: ChatMessageBase}

export type AddMessageQueryType = {
  passphrase: string
  hostname: string
  threadId: string
  message: string
}

export type AddMessageReturnType = { message: ChatMessageBase}

export const apiSlice = createApi({
  reducerPath: 'serverApi',
  baseQuery: fetchBaseQuery({ baseUrl: process.env.REACT_APP_BACKEND_URL }),
  endpoints: (builder) => ({
    startChat: builder.mutation<StartChatReturnType, StartChatQueryType>({
      query: (startChatDto) => ({
        url: '/api/start_chat',
        method: 'POST',
        body: startChatDto,
      }),
    }),
    addMessage: builder.mutation<AddMessageReturnType, AddMessageQueryType>({
      query: (addMessageDto) => ({
        url: '/api/add_chat_message',
        method: 'POST',
        body: addMessageDto,
      }),
    }),
  }),
})

export const {  useStartChatMutation, useAddMessageMutation } = apiSlice
