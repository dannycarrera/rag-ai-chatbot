import React, { Fragment, useEffect, useRef, useState } from 'react'
import {
  Alert,
  Avatar,
  Badge,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Stack,
  styled,
  Typography,
} from '@mui/material'
import Grid from '@mui/material/Grid2'
import PersonIcon from '@mui/icons-material/Person'
import { ChatBubble } from './ChatBubble'
import { addMessage, ChatMessage, ChatState } from '../../store/chatSlice'
import { useDispatch } from 'react-redux'
import { useAddMessageMutation } from '../../store/apiSlice'

const StyledBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: '#44b700',
    color: '#44b700',
    boxShadow: `0 0 0 2px ${theme.palette.background.paper}`,
    '&::after': {
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      borderRadius: '50%',
      animation: 'ripple 1.2s infinite ease-in-out',
      border: '1px solid currentColor',
      content: '""',
    },
  },
}))

const AIAvatar = () => (
  <StyledBadge
    overlap="circular"
    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
    variant="dot"
  >
    <Avatar>
      <PersonIcon />
    </Avatar>
  </StyledBadge>
)

export function AIMessage({
  state,
  message,
  setIsSubmittingByClick,
}: {
  state: ChatState
  message: ChatMessage
  setIsSubmittingByClick: React.Dispatch<React.SetStateAction<boolean>>
}) {
  const isMountedRef = useRef(false)
  const [clickDisabled, setClickDisabled] = useState(state.messages.length > 1)
  const [error, setError] = useState<string | null>(null)
  const [addMessageMutation] = useAddMessageMutation()

  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
    }
  }, [])

  useEffect(() => {
    if (clickDisabled && error) setError(null)
  }, [clickDisabled, error, setError])

  const dispatch = useDispatch()

  const handleClick = async (
    event: React.MouseEvent<HTMLDivElement, MouseEvent>,
    index: number
  ) => {
    try {
      if (
        state.passphrase &&
        state.hostname &&
        state.threadId &&
        message.mc_options
      ) {
        setIsSubmittingByClick(true)
        setClickDisabled(true)
        const content = message.mc_options[index]
        const response = await addMessageMutation({
          passphrase: state.passphrase,
          hostname: state.hostname,
          threadId: state.threadId,
          message: content,
        }).unwrap()

        // Do nothing if unmounted
        if (!isMountedRef.current) return
        const addUserMsgRespDto: ChatMessage = {
          from: 'user',
          content,
        }

        dispatch(addMessage(addUserMsgRespDto))

        const addMsgRespDto: ChatMessage = { from: 'ai', ...response.message }
        dispatch(addMessage(addMsgRespDto))
        setIsSubmittingByClick(false)
      }
    } catch (error: any) {
      let message = 'Something went wrong. Please try again later.'
      if (error.status === 429 && error.data.type === 'insufficient_quota') {
        message =
          'Insufficient OpenAI quota. Please try again after purchasing more credits.'
      }
      setError(message)
      setIsSubmittingByClick(false)
      setClickDisabled(false)
    }
  }
  return (
    <Fragment>
      <Grid size={8}>
        <Stack direction="row" spacing={1}>
          <Box>
            <AIAvatar />
          </Box>

          <ChatBubble messageType="ai">
            <Typography whiteSpace="pre-wrap" variant="body2" align="left">
              {message.content}
            </Typography>

            <List>
              {message.mc_options &&
                message.mc_options.map((o, oi) => (
                  <ListItem key={oi} disablePadding>
                    <ListItemButton
                      disabled={clickDisabled}
                      onClick={(e) => handleClick(e, oi)}
                    >
                      <ListItemText primary={o} />
                    </ListItemButton>
                  </ListItem>
                ))}
            </List>
            {error && (
              <Alert sx={{ alignSelf: 'center' }} severity="error">
                {error}
              </Alert>
            )}
          </ChatBubble>
        </Stack>
      </Grid>
      <Grid size={4}></Grid>
    </Fragment>
  )
}
