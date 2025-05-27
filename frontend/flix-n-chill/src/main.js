import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/font.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import axios from 'axios'

import App from './App.vue'
import router from './router'


axios.defaults.baseURL = '/api'


const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
