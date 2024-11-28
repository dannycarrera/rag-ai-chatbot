import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

export interface UrlState {
  url: string | null
}

const initialState: UrlState = {
  url: null,
}


// export const fetchUrlStartProcessing = createAsyncThunk<UrlState[]>(
//   'url/fetchUrlStartProcessing',
//   async (input, { extra }) => {
//     try {
//       // const { userServices } = input

//       const dtoContacts: ContactDto[] = await userServices.contacts.all()

//       return dtoContacts
//     } catch (err) {
//       console.error('Failed fetching initial contacts', err)
//       throw err
//     }
//   }
// )

// export const urlSlice = createSlice({
//   name: 'url',
//   initialState,
//   reducers: {
//     blah: (state) => {
    
//       state.url = "blah"
//     },
   
//   },
// })

// // Action creators are generated for each case reducer function
// export const { blah } = urlSlice.actions

// export default urlSlice.reducer