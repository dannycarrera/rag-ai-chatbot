import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid2,
  Typography
} from '@mui/material'
import React, { useState } from 'react'
import { useDispatch } from 'react-redux'
import {
  resetChat
} from '../../store/chatSlice'
import { persistor } from '../../store/store'

function ConfirmNewAgentDialog({
  open,
  setOpen,
}: {
  open: boolean
  setOpen: React.Dispatch<React.SetStateAction<boolean>>
}) {
  const dispatch = useDispatch()

  const handleContinue = () => {
    persistor.purge()
    dispatch(resetChat())
    setOpen(false)
  }

  return (
    <Dialog
      open={open}
      onClose={handleContinue}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title">
        {'Create new Chat Agent?'}
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="alert-dialog-description">
          Are you sure you want to create a new Agent? All chat history will be
          lost.
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleContinue}>Continue</Button>
        <Button onClick={() => setOpen(false)} autoFocus>
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default function ChatHeader({ url }: { url: string }) {
  const [open, setOpen] = useState(false)

  const handleClickOpen = () => {
    setOpen(true)
  }

  return (
    <React.Fragment>
      <ConfirmNewAgentDialog open={open} setOpen={setOpen} />
      <Grid2 container direction="row" sx={{ backgroundColor: 'gray' }}>
        <Grid2 padding={1}>
          <Typography>{url}</Typography>
        </Grid2>
        <Grid2 padding={1} flexGrow={1}>
          <Typography>AI Chat Sales Agent</Typography>
        </Grid2>
        <Grid2 padding={1} sx={{ display: 'flex', alignItems: 'center' }}>
          <Button variant="outlined" onClick={handleClickOpen}>
            New Agent
          </Button>
        </Grid2>
      </Grid2>
    </React.Fragment>
  )
}