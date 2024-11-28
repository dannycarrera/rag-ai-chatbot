import SendIcon from '@mui/icons-material/Send'
import { LoadingButton } from '@mui/lab'
import { FormControl, Grid2, TextField } from '@mui/material'
import { useEffect, useRef } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { useDispatch } from 'react-redux'
import { useAddMessageMutation } from '../../store/apiSlice'
import { addMessage, ChatMessage, ChatState } from '../../store/chatSlice'

export default function ChatFooter({
  state,
  isSubmittingByClick,
}: {
  state: ChatState
  isSubmittingByClick: boolean
}) {
  const {
    register,
    handleSubmit,
    control,
    reset,
    setError,
    setFocus,
    getValues,
    trigger,
    clearErrors,
    formState: { isSubmitting, isValid, isValidating, errors, isDirty },
  } = useForm({ mode: 'all' })

  const msgLengthRef = useRef<number>(state.messages.length)
  const dispatch = useDispatch()
  const [addMessageMutation] = useAddMessageMutation()
  const isMountedRef = useRef(false)

  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
    }
  }, [])

  useEffect(() => {
    if (msgLengthRef.current < state.messages.length) {
      setTimeout(() => {
        clearErrors()
        setFocus('message')
        trigger()
      }, 0)
      msgLengthRef.current = state.messages.length
    }
  }, [msgLengthRef, state])

  const onSubmit = handleSubmit(async (data) => {
    try {
      const values = getValues()

      const message = values.message.trim()
      if (isValid && state.passphrase && state.hostname && state.threadId) {
        const response = await addMessageMutation({
          passphrase: state.passphrase,
          hostname: state.hostname,
          threadId: state.threadId,
          message,
        }).unwrap()

        // Do nothing if unmounted
        if (!isMountedRef.current) return

        // setTimeout needed else isValid won't reset
        setTimeout(() => {
          reset()
        }, 0)

        const addUserMsgRespDto: ChatMessage = {
          from: 'user',
          content: message,
        }

        dispatch(addMessage(addUserMsgRespDto))

        const addMsgRespDto: ChatMessage = { from: 'ai', ...response.message }
        dispatch(addMessage(addMsgRespDto))
      }
    } catch (error: any) {
      console.error(error)
      let type = '500'
      let message = 'Something went wrong. Please try again later.'
      if (error.status === 429 && error.data.type === 'insufficient_quota') {
        type = 'insufficient_quota'
        message =
          'Insufficient OpenAI quota. Please try again after purchasing more credits.'
      }

      // setTimeout required to setFocus and trigger
      setTimeout(() => {
        setError('root.serverError', {
          type,
          message,
        })
        setFocus('message')
        trigger()
      }, 0)
    }
  })

  return (
    <form onSubmit={onSubmit}>
      <Grid2 container direction="row" sx={{ backgroundColor: 'gray' }}>
        <Grid2 padding={1} flexGrow={1}>
          <FormControl fullWidth variant="outlined">
            <Controller
              name="message"
              render={({ field: { ref, ...field }, fieldState: { error } }) => {
                return (
                  <TextField
                    {...register('message')}
                    {...field}
                    id="message"
                    fullWidth
                    multiline
                    maxRows={6}
                    variant="outlined"
                    disabled={isSubmitting || isSubmittingByClick}
                    error={!!errors.root}
                    helperText={errors.root && errors.root.serverError.message}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault()
                        const values = getValues()
                        if (values.message && values.message.trim() !== '') {
                          onSubmit(e)
                        }
                      }
                    }}
                  />
                )
              }}
              control={control}
              defaultValue=""
              rules={{
                required: 'asd',
              }}
            />
          </FormControl>
        </Grid2>
        <Grid2 padding={1} sx={{ display: 'flex', alignItems: 'center' }}>
          <LoadingButton
            disabled={(!isValid && !isSubmitting) || isSubmittingByClick}
            loading={isSubmitting || isSubmittingByClick}
            startIcon={<SendIcon />}
            variant="contained"
            color="primary"
            type="submit"
          ></LoadingButton>
        </Grid2>
      </Grid2>
    </form>
  )
}
