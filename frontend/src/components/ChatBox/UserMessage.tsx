import  { Fragment } from 'react'
import {
  Stack,
  Box,
  Typography,
  Avatar,
} from '@mui/material'
import { ChatBubble } from './ChatBubble'
import Grid from '@mui/material/Grid2'
import PersonIcon from '@mui/icons-material/Person'
import { ChatMessage } from '../../store/chatSlice'

const UserAvatar = () => (
  <Avatar>
    <PersonIcon />
  </Avatar>
)

export function UserMessage({ message }: { message: ChatMessage }) {
  return (
    <Fragment>
      <Grid size={4}></Grid>
      <Grid size={8}>
        <Stack direction="row-reverse" spacing={1}>
          <Box>
            <UserAvatar />
          </Box>
          <ChatBubble messageType="user">
            <Typography whiteSpace='pre-wrap' variant="body2" align="right">
              {message.content}
            </Typography>
          </ChatBubble>
        </Stack>
      </Grid>
    </Fragment>
  )
}
