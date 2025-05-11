import {createRouter, createWebHistory, RouteRecordRaw} from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import TestView from '@/views/TestView.vue'
import ChooseTestView from '@/views/ChooseTestView.vue'
import TestDetailView from '@/views/TestDetailView.vue';
import PublicTestView from '@/views/PublicTestView.vue'
import DefaultTestsView from '@/views/DefaultTestsView.vue'
import TestResponsesView from '@/views/TestResponsesView.vue'
import VisualizeDrawing from '@/views/VisualizeDrawing.vue'
import DrawingViewWithRecording from '@/views/DrawingViewWithRecording.vue'
import DefaultTestView from '@/views/DefaultTestView.vue'
const routes: Array<RouteRecordRaw> = [
    {path: '/', component: HomeView},
    {path: '/login', component: LoginView},
    {path: '/register', component: RegisterView},
    {path: '/draw', component: DrawingViewWithRecording},
    {path: '/tests', component: TestView },
    {path: '/choosetest', component: ChooseTestView},
    {path: '/tests/:id',name: 'testDetail',component: TestDetailView},
    {path: '/tests/:id/public',component: PublicTestView,},
    {path: '/tests/:id/responses',component: TestResponsesView,},
    {path: '/default', component: DefaultTestsView},
    {path: '/draw/:id', component: VisualizeDrawing},
    {path: '/defaulttest/:id', component: DefaultTestView},

]
// umožňuje používať moderné URL bez hash (#)
const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
})

export default router
