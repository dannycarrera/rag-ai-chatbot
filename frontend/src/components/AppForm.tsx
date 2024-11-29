import { useEffect, useRef } from 'react'
import { useForm, Controller } from 'react-hook-form'
import FormControl from '@mui/material/FormControl'
import TextField from '@mui/material/TextField'
import urlSafe from 'url-regex-safe'
import { useStartChatMutation } from '../store/apiSlice'
import { useDispatch } from 'react-redux'
import { startChat, StartChatPayloadType } from '../store/chatSlice'
import { LoadingButton } from '@mui/lab'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import { Alert, Box, Stack } from '@mui/material'

export default function AppForm({}) {
  const isMountedRef = useRef(false)

  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
    }
  }, [])

  const {
    register,
    handleSubmit,
    control,
    getValues,
    setError,
    trigger,
    formState: { isSubmitting, isValid, errors },
  } = useForm({ mode: 'all' })

  const dispatch = useDispatch()
  const [startChatMutation] = useStartChatMutation()

  const validUrlText = 'Enter a valid URL ie. https://holoinvites.com'
  const validateUrl = (value: string) => {
    if (!value.trim().startsWith('https://'))
      return `${validUrlText}. Only https sites are currently supported.`
    const isUrl = urlSafe({}).test(value)
    if (!isUrl) return validUrlText
    return true
  }

  const onSubmit = handleSubmit(async (data) => {
    try {
      const values = getValues()
      const url = values.url.trim()
      const passphrase = values.passphrase
      if (isValid) {
        const response = await startChatMutation({ url, passphrase }).unwrap()

        // Do nothing if unmounted
        if (!isMountedRef.current) return
        const startChatRespDto: StartChatPayloadType = {
          passphrase,
          hostname: new URL(url).hostname,
          threadId: response.thread_id,
          message: { from: 'ai', ...response.message },
        }
        dispatch(startChat(startChatRespDto))
      }
    } catch (error: any) {
      let name = 'root.serverError'
      let type = '500'
      let message = 'Something went wrong. Please try again later.'
      if (error.status === 401) {
        name = 'passphrase'
        type = 'value'
        message = 'Incorrect passphrase'
      } else if (
        error.status === 429 &&
        error.data.type === 'insufficient_quota'
      ) {
        type = 'insufficient_quota'
        message = 'Insufficient OpenAI quota'
      }
      // setTimeout required for trigger
      setTimeout(() => {
        setError(name, {
          type,
          message,
        })
        if (error.status !== 401) trigger()
      }, 0)
    }
  })

  return (
    <Box sx={{ minWidth: 500 }}>
      <form onSubmit={onSubmit}>
        <FormControl fullWidth variant="outlined">
          <Stack spacing={1}>
            <Controller
              name="passphrase"
              render={({ field: { ref, ...field }, fieldState: { error } }) => {
                return (
                  <TextField
                    {...register('passphrase')}
                    {...field}
                    id="passphrase"
                    variant="outlined"
                    label="Passphrase"
                    type="password"
                    disabled={isSubmitting}
                    error={!!error}
                    helperText={
                      error ? error?.message : 'Your secret passphrase'
                    }
                  />
                )
              }}
              control={control}
              defaultValue=""
              rules={{
                required: 'Passphrase is required',
                pattern: {
                  value: /^[A-Za-z0-9_]+$/,
                  message:
                    'Only alphanumeric characters and underscores are allowed',
                },
              }}
            />
            <Controller
              name="url"
              render={({ field: { ref, ...field }, fieldState: { error } }) => {
                return (
                  <TextField
                    {...register('url')}
                    {...field}
                    id="url"
                    variant="outlined"
                    label="URL"
                    disabled={isSubmitting}
                    error={!!error}
                    helperText={error ? error?.message : validUrlText}
                  />
                )
              }}
              control={control}
              defaultValue=""
              rules={{
                required: validUrlText,
                validate: validateUrl,
              }}
            />
            <LoadingButton
              sx={{ alignSelf: 'center' }}
              disabled={!isValid && !isSubmitting}
              loading={isSubmitting}
              loadingPosition="start"
              startIcon={<PlayArrowIcon />}
              variant="contained"
              color="primary"
              type="submit"
            >
              Start
            </LoadingButton>
            {errors && errors.root && (
              <Alert sx={{ alignSelf: 'center' }} severity="error">
                {errors.root.serverError.message}
              </Alert>
            )}
          </Stack>
        </FormControl>
      </form>
    </Box>
  )
}
