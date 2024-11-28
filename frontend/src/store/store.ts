import { combineReducers, configureStore } from '@reduxjs/toolkit'
import { apiSlice } from './apiSlice'
import chatReducer, { initialChatState } from './chatSlice'
import { persistStore, persistReducer, FLUSH, PAUSE, PERSIST, PURGE, REGISTER, REHYDRATE } from 'redux-persist'
import storageSession from 'redux-persist/lib/storage/session'

const persistConfig = {
  key: 'root',
  storage: storageSession,
}

const reducers = combineReducers({
  [apiSlice.reducerPath]: apiSlice.reducer,
  chat: chatReducer,
})

const persistedReducer = persistReducer(persistConfig, reducers)

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }).concat(apiSlice.middleware),
})

export let persistor = persistStore(store)

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
