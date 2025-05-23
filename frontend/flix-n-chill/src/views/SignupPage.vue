<template>
    <div class="signup-page">
        <!-- 배경 그라데이션 -->
        <div class="background-gradient"></div>

        <!-- 메인 컨테이너 -->
        <div class="signup-container">
            <div class="signup-card">
                <!-- 헤더 -->
                <div class="signup-header">
                    <h1 class="signup-title">회원가입</h1>
                    <p class="signup-subtitle">새로운 계정을 만들어보세요</p>
                </div>

                <!-- 회원가입 폼 -->
                <form @submit.prevent="handleSubmit" class="signup-form">
                    <!-- 이메일 입력 -->
                    <div class="form-group">
                        <label for="email" class="form-label">이메일 주소</label>
                        <div class="input-wrapper">
                            <input id="email" v-model="formData.email" type="email" class="form-input" :class="{
                                'error': errors.email,
                                'success': !errors.email && formData.email && isEmailValid
                            }" placeholder="example@email.com" @blur="validateEmail" @input="clearError('email')">
                            <button type="button" class="check-duplicate-btn" @click="checkEmailDuplicate"
                                :disabled="!isEmailValid || isCheckingEmail">
                                {{ isCheckingEmail ? '확인중...' : '중복확인' }}
                            </button>
                        </div>
                        <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
                        <div v-if="emailCheckResult" class="success-message">{{ emailCheckResult }}</div>
                    </div>

                    <!-- 비밀번호 입력 -->
                    <div class="form-group">
                        <label for="password" class="form-label">비밀번호</label>
                        <div class="input-wrapper">
                            <input id="password" v-model="formData.password" :type="showPassword ? 'text' : 'password'"
                                class="form-input" :class="{
                                    'error': errors.password,
                                    'success': !errors.password && formData.password && getPasswordStrength() >= 3
                                }" placeholder="8자 이상 입력해주세요" @input="validatePassword">
                            <button type="button" class="toggle-password-btn" @click="showPassword = !showPassword">
                                <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                            </button>
                        </div>
                        <div v-if="errors.password" class="error-message">{{ errors.password }}</div>

                        <!-- 비밀번호 강도 표시기 -->
                        <div v-if="formData.password" class="password-strength">
                            <div class="strength-bar">
                                <div class="strength-fill" :class="getPasswordStrengthClass()"
                                    :style="{ width: (getPasswordStrength() / 4) * 100 + '%' }"></div>
                            </div>
                            <p class="strength-text" :class="getPasswordStrengthClass()">
                                {{ getPasswordStrengthText() }}
                            </p>
                        </div>
                    </div>

                    <!-- 비밀번호 확인 -->
                    <div class="form-group">
                        <label for="confirmPassword" class="form-label">비밀번호 확인</label>
                        <div class="input-wrapper">
                            <input id="confirmPassword" v-model="formData.confirmPassword"
                                :type="showConfirmPassword ? 'text' : 'password'" class="form-input" :class="{
                                    'error': errors.confirmPassword,
                                    'success': !errors.confirmPassword && formData.confirmPassword && formData.password === formData.confirmPassword
                                }" placeholder="비밀번호를 다시 입력해주세요" @blur="validateConfirmPassword"
                                @input="clearError('confirmPassword')">
                            <button type="button" class="toggle-password-btn"
                                @click="showConfirmPassword = !showConfirmPassword">
                                <i :class="showConfirmPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                            </button>
                        </div>
                        <div v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</div>
                    </div>

                    <!-- 닉네임 입력 -->
                    <div class="form-group">
                        <label for="nickname" class="form-label">닉네임</label>
                        <input id="nickname" v-model="formData.nickname" type="text" class="form-input" :class="{
                            'error': errors.nickname,
                            'success': !errors.nickname && formData.nickname && formData.nickname.length >= 2
                        }" placeholder="프로필에 표시될 닉네임" @blur="validateNickname" @input="clearError('nickname')">
                        <div v-if="errors.nickname" class="error-message">{{ errors.nickname }}</div>
                    </div>

                    <!-- 생년월일 입력 -->
                    <div class="form-group">
                        <label for="birthdate" class="form-label">생년월일</label>
                        <input id="birthdate" v-model="formData.birthdate" type="date" class="form-input" :class="{
                            'error': errors.birthdate,
                            'success': !errors.birthdate && formData.birthdate
                        }" @blur="validateBirthdate" @input="clearError('birthdate')">
                        <div v-if="errors.birthdate" class="error-message">{{ errors.birthdate }}</div>
                    </div>

                    <!-- 약관 동의 -->
                    <!-- 기존 약관 동의 부분 수정 -->
                    <div class="terms-section">
                        <div class="checkbox-group">
                            <input id="agreeTerms" v-model="agreeTerms" type="checkbox" class="checkbox-input">
                            <label for="agreeTerms" class="checkbox-label">
                                <span class="checkbox-custom"></span>
                                <span class="checkbox-text">
                                    <a href="#" class="terms-link" @click.prevent="showTermsModal = true">이용약관</a> 및
                                    <a href="#" class="terms-link"
                                        @click.prevent="showPrivacyModal = true">개인정보처리방침</a>에 동의합니다
                                </span>
                            </label>
                        </div>
                        <div v-if="errors.terms" class="error-message">{{ errors.terms }}</div>
                    </div>

                    <!-- 이용약관 모달 -->
                    <div v-if="showTermsModal" class="modal-overlay" @click="showTermsModal = false">
                        <div class="modal-content" @click.stop>
                            <div class="modal-header">
                                <h2 class="modal-title">이용약관</h2>
                                <button class="modal-close-btn" @click="showTermsModal = false">
                                    <i class="bi bi-x-lg"></i>
                                </button>
                            </div>
                            <div class="modal-body">
                                <div class="terms-content">
                                    <h3>제1조 (목적)</h3>
                                    <p>이 약관은 [서비스명](이하 "회사")이 제공하는 온라인 서비스의 이용과 관련하여 회사와 이용자 간의 권리, 의무 및 책임사항을 규정함을 목적으로
                                        합니다.</p>

                                    <h3>제2조 (용어의 정의)</h3>
                                    <p>① "서비스"란 회사가 제공하는 모든 온라인 서비스를 의미합니다.</p>
                                    <p>② "이용자"란 이 약관에 따라 회사가 제공하는 서비스를 받는 회원 및 비회원을 말합니다.</p>
                                    <p>③ "회원"이란 회사에 개인정보를 제공하여 회원등록을 한 자로서, 회사의 정보를 지속적으로 제공받으며, 회사가 제공하는 서비스를 계속적으로 이용할
                                        수 있는 자를 말합니다.</p>

                                    <h3>제3조 (약관의 효력 및 변경)</h3>
                                    <p>① 이 약관은 서비스를 이용하고자 하는 모든 이용자에 대하여 그 효력을 발생합니다.</p>
                                    <p>② 회사는 합리적인 사유가 발생할 경우에는 이 약관을 변경할 수 있으며, 약관을 변경하는 경우에는 적용일자 및 개정사유를 명시하여 현행약관과 함께
                                        서비스의 초기화면에 그 적용일자 7일 이전부터 적용일자 전일까지 공지합니다.</p>

                                    <h3>제4조 (서비스의 제공 및 변경)</h3>
                                    <p>① 회사는 다음과 같은 업무를 수행합니다:</p>
                                    <ul>
                                        <li>온라인 서비스 제공</li>
                                        <li>기타 회사가 정하는 업무</li>
                                    </ul>
                                    <p>② 회사는 운영상, 기술상의 필요에 따라 제공하고 있는 전부 또는 일부 서비스를 변경할 수 있습니다.</p>

                                    <h3>제5조 (서비스의 중단)</h3>
                                    <p>회사는 컴퓨터 등 정보통신설비의 보수점검·교체 및 고장, 통신의 두절 등의 사유가 발생한 경우에는 서비스의 제공을 일시적으로 중단할 수 있습니다.
                                    </p>

                                    <h3>제6조 (회원가입)</h3>
                                    <p>① 이용자는 회사가 정한 가입 양식에 따라 회원정보를 기입한 후 이 약관에 동의한다는 의사표시를 함으로서 회원가입을 신청합니다.</p>
                                    <p>② 회사는 제1항과 같이 회원으로 가입할 것을 신청한 이용자 중 다음 각 호에 해당하지 않는 한 회원으로 등록합니다:</p>
                                    <ul>
                                        <li>가입신청자가 이 약관에 의하여 이전에 회원자격을 상실한 적이 있는 경우</li>
                                        <li>등록 내용에 허위, 기재누락, 오기가 있는 경우</li>
                                        <li>기타 회원으로 등록하는 것이 회사의 기술상 현저히 지장이 있다고 판단되는 경우</li>
                                    </ul>

                                    <h3>제7조 (개인정보보호)</h3>
                                    <p>회사는 관련법령이 정하는 바에 따라 이용자의 개인정보를 보호하기 위해 노력합니다. 개인정보의 보호 및 사용에 대해서는 관련법령 및 회사의
                                        개인정보처리방침이 적용됩니다.</p>

                                    <h3>제8조 (회사의 의무)</h3>
                                    <p>① 회사는 법령과 이 약관이 금지하거나 공서양속에 반하는 행위를 하지 않으며 이 약관이 정하는 바에 따라 지속적이고, 안정적으로 서비스를 제공하기
                                        위해서 최선을 다하여 노력합니다.</p>
                                    <p>② 회사는 이용자가 안전하게 인터넷 서비스를 이용할 수 있도록 이용자의 개인정보보호를 위한 보안시스템을 구축합니다.</p>

                                    <h3>제9조 (이용자의 의무)</h3>
                                    <p>① 이용자는 다음 행위를 하여서는 안 됩니다:</p>
                                    <ul>
                                        <li>신청 또는 변경시 허위내용의 등록</li>
                                        <li>타인의 정보 도용</li>
                                        <li>회사가 게시한 정보의 변경</li>
                                        <li>회사가 정한 정보 이외의 정보(컴퓨터 프로그램 등) 등의 송신 또는 게시</li>
                                        <li>회사 기타 제3자의 저작권 등 지적재산권에 대한 침해</li>
                                        <li>회사 기타 제3자의 명예를 손상시키거나 업무를 방해하는 행위</li>
                                        <li>외설 또는 폭력적인 메시지, 화상, 음성, 기타 공서양속에 반하는 정보를 서비스에 공개 또는 게시하는 행위</li>
                                    </ul>

                                    <h3>제10조 (저작권의 귀속 및 이용제한)</h3>
                                    <p>① 회사가 작성한 저작물에 대한 저작권 기타 지적재산권은 회사에 귀속합니다.</p>
                                    <p>② 이용자는 서비스를 이용함으로써 얻은 정보 중 회사에게 지적재산권이 귀속된 정보를 회사의 사전 승낙 없이 복제, 송신, 출판, 배포, 방송 기타
                                        방법에 의하여 영리목적으로 이용하거나 제3자에게 이용하게 하여서는 안됩니다.</p>

                                    <h3>제11조 (분쟁해결)</h3>
                                    <p>① 회사는 이용자가 제기하는 정당한 의견이나 불만을 반영하고 그 피해를 보상처리하기 위하여 피해보상처리기구를 설치·운영합니다.</p>
                                    <p>② 회사와 이용자 간에 발생한 전자상거래 분쟁에 관한 소송은 서울중앙지방법원을 관할 법원으로 합니다.</p>

                                    <p class="terms-date"><strong>본 약관은 2024년 1월 1일부터 시행됩니다.</strong></p>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button class="modal-btn secondary" @click="showTermsModal = false">닫기</button>
                                <button class="modal-btn primary" @click="agreeToTerms">동의하기</button>
                            </div>
                        </div>
                    </div>

                    <!-- 개인정보처리방침 모달 -->
                    <div v-if="showPrivacyModal" class="modal-overlay" @click="showPrivacyModal = false">
                        <div class="modal-content" @click.stop>
                            <div class="modal-header">
                                <h2 class="modal-title">개인정보처리방침</h2>
                                <button class="modal-close-btn" @click="showPrivacyModal = false">
                                    <i class="bi bi-x-lg"></i>
                                </button>
                            </div>
                            <div class="modal-body">
                                <div class="terms-content">
                                    <h3>개인정보 처리방침</h3>
                                    <p>[서비스명](이하 "회사")은 개인정보보호법에 따라 이용자의 개인정보 보호 및 권익을 보호하고 개인정보와 관련한 이용자의 고충을 원활하게 처리할
                                        수 있도록 다음과 같은 처리방침을 두고 있습니다.</p>

                                    <h3>제1조 (개인정보의 처리목적)</h3>
                                    <p>회사는 다음의 목적을 위하여 개인정보를 처리합니다. 처리하고 있는 개인정보는 다음의 목적 이외의 용도로는 이용되지 않으며, 이용 목적이 변경되는
                                        경우에는 개인정보보호법 제18조에 따라 별도의 동의를 받는 등 필요한 조치를 이행할 예정입니다.</p>
                                    <ul>
                                        <li><strong>회원가입 및 관리:</strong> 회원 가입의사 확인, 회원제 서비스 제공에 따른 본인 식별·인증, 회원자격 유지·관리,
                                            서비스 부정이용 방지, 만14세 미만 아동의 개인정보 처리 시 법정대리인의 동의여부 확인, 각종 고지·통지, 고충처리 목적으로 개인정보를
                                            처리합니다.</li>
                                        <li><strong>서비스 제공:</strong> 콘텐츠 제공, 특정 맞춤서비스 제공, 본인인증, 연령인증, 요금결제·정산, 채권추심 목적으로
                                            개인정보를 처리합니다.</li>
                                        <li><strong>마케팅 및 광고:</strong> 신규 서비스(제품) 개발 및 맞춤 서비스 제공, 이벤트 및 광고성 정보 제공 및 참여기회
                                            제공, 인구통계학적 특성에 따른 서비스 제공 및 광고 게재, 서비스의 유효성 확인, 접속빈도 파악 또는 회원의 서비스 이용에 대한 통계
                                            목적으로 개인정보를 처리합니다.</li>
                                    </ul>

                                    <h3>제2조 (개인정보의 처리 및 보유기간)</h3>
                                    <p>① 회사는 법령에 따른 개인정보 보유·이용기간 또는 정보주체로부터 개인정보를 수집 시에 동의받은 개인정보 보유·이용기간 내에서 개인정보를
                                        처리·보유합니다.</p>
                                    <p>② 각각의 개인정보 처리 및 보유 기간은 다음과 같습니다:</p>
                                    <ul>
                                        <li><strong>회원가입 및 관리:</strong> 회원탈퇴 시까지 (단, 관계법령 위반에 따른 수사·조사 등이 진행중인 경우에는 해당
                                            수사·조사 종료시까지)</li>
                                        <li><strong>서비스 제공:</strong> 서비스 이용계약 또는 회원가입 해지시까지, 다만 채권·채무관계 잔존시에는 해당 채권·채무관계
                                            정산시까지</li>
                                        <li><strong>부정이용 기록:</strong> 5년</li>
                                    </ul>

                                    <h3>제3조 (처리하는 개인정보의 항목)</h3>
                                    <p>회사는 다음의 개인정보 항목을 처리하고 있습니다:</p>
                                    <ul>
                                        <li><strong>필수항목:</strong> 이메일주소, 비밀번호, 닉네임, 생년월일</li>
                                        <li><strong>선택항목:</strong> 프로필 사진, 전화번호</li>
                                        <li><strong>자동수집항목:</strong> IP주소, 쿠키, MAC주소, 서비스 이용기록, 방문기록, 불량 이용기록 등</li>
                                    </ul>

                                    <h3>제4조 (개인정보의 제3자 제공)</h3>
                                    <p>① 회사는 개인정보를 제1조(개인정보의 처리목적)에서 명시한 범위 내에서만 처리하며, 이용자의 동의, 법률의 특별한 규정 등 개인정보보호법
                                        제17조 및 제18조에 해당하는 경우에만 개인정보를 제3자에게 제공합니다.</p>

                                    <h3>제5조 (개인정보처리의 위탁)</h3>
                                    <p>① 회사는 원활한 개인정보 업무처리를 위하여 다음과 같이 개인정보 처리업무를 위탁하고 있습니다:</p>
                                    <ul>
                                        <li><strong>이메일 발송 업무:</strong> [위탁업체명] - 개인정보 항목(이메일주소), 보유기간(위탁계약 종료시까지)</li>
                                        <li><strong>결제처리 업무:</strong> [결제대행업체명] - 개인정보 항목(신용카드정보, 은행계좌정보), 보유기간(결제완료 후
                                            5년)</li>
                                    </ul>

                                    <h3>제6조 (이용자의 권리·의무 및 행사방법)</h3>
                                    <p>① 이용자는 회사에 대해 언제든지 다음 각 호의 개인정보 보호 관련 권리를 행사할 수 있습니다:</p>
                                    <ul>
                                        <li>개인정보 처리정지 요구</li>
                                        <li>개인정보 열람요구</li>
                                        <li>개인정보 정정·삭제요구</li>
                                        <li>개인정보 처리정지 요구</li>
                                    </ul>
                                    <p>② 제1항에 따른 권리 행사는 개인정보보호법 시행규칙 별지 제8호 서식에 따라 서면, 전자우편, 모사전송(FAX) 등을 통하여 하실 수 있으며
                                        회사는 이에 대해 지체없이 조치하겠습니다.</p>

                                    <h3>제7조 (개인정보의 파기)</h3>
                                    <p>① 회사는 개인정보 보유기간의 경과, 처리목적 달성 등 개인정보가 불필요하게 되었을 때에는 지체없이 해당 개인정보를 파기합니다.</p>
                                    <p>② 개인정보 파기의 절차 및 방법은 다음과 같습니다:</p>
                                    <ul>
                                        <li><strong>파기절차:</strong> 회사는 파기 사유가 발생한 개인정보를 선정하고, 개인정보 보호책임자의 승인을 받아 개인정보를
                                            파기합니다.</li>
                                        <li><strong>파기방법:</strong> 전자적 파일 형태의 정보는 기록을 재생할 수 없는 기술적 방법을 사용합니다.</li>
                                    </ul>

                                    <h3>제8조 (개인정보의 안전성 확보조치)</h3>
                                    <p>회사는 개인정보의 안전성 확보를 위해 다음과 같은 조치를 취하고 있습니다:</p>
                                    <ul>
                                        <li>관리적 조치: 내부관리계획 수립·시행, 정기적 직원 교육 등</li>
                                        <li>기술적 조치: 개인정보처리시스템 등의 접근권한 관리, 접근통제시스템 설치, 고유식별정보 등의 암호화, 보안프로그램 설치</li>
                                        <li>물리적 조치: 전산실, 자료보관실 등의 접근통제</li>
                                    </ul>

                                    <h3>제9조 (개인정보보호책임자)</h3>
                                    <p>① 회사는 개인정보 처리에 관한 업무를 총괄해서 책임지고, 개인정보 처리와 관련한 정보주체의 불만처리 및 피해구제 등을 위하여 아래와 같이
                                        개인정보보호책임자를 지정하고 있습니다:</p>
                                    <ul>
                                        <li><strong>개인정보보호책임자:</strong> [담당자명]</li>
                                        <li><strong>연락처:</strong> [전화번호], [이메일주소]</li>
                                    </ul>

                                    <h3>제10조 (개정 전 고지의무)</h3>
                                    <p>이 개인정보처리방침은 시행일로부터 적용되며, 법령 및 방침에 따른 변경내용의 추가, 삭제 및 정정이 있는 경우에는 변경사항의 시행 7일 전부터
                                        공지사항을 통하여 고지할 것입니다.</p>

                                    <p class="terms-date"><strong>본 개인정보처리방침은 2024년 1월 1일부터 시행됩니다.</strong></p>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button class="modal-btn secondary" @click="showPrivacyModal = false">닫기</button>
                                <button class="modal-btn primary" @click="agreeToPrivacy">동의하기</button>
                            </div>
                        </div>
                    </div>

                    <!-- 회원가입 버튼 -->
                    <button type="submit" class="signup-btn" :disabled="!isFormValid || isSubmitting">
                        <span v-if="isSubmitting" class="loading-spinner"></span>
                        {{ isSubmitting ? '가입 중...' : '회원가입' }}
                    </button>
                </form>

                <!-- 로그인 링크 -->
                <div class="login-link">
                    <p>이미 계정이 있으신가요?
                        <router-link to="/login" class="link">로그인</router-link>
                    </p>
                </div>
            </div>
        </div>

        <!-- 성공 팝업 -->
        <div v-if="showSuccessPopup" class="popup-overlay" @click="closeSuccessPopup">
            <div class="popup-content" @click.stop>
                <div class="popup-header">
                    <div class="success-icon">
                        <i class="bi bi-check-circle-fill"></i>
                    </div>
                    <h2 class="popup-title">회원가입 완료!</h2>
                    <p class="popup-message">
                        환영합니다, {{ formData.nickname }}님!<br>
                        이제 로그인하여 서비스를 이용하실 수 있습니다.
                    </p>
                </div>
                <div class="popup-actions">
                    <button class="popup-btn primary" @click="goToLogin">로그인하기</button>
                    <button class="popup-btn secondary" @click="closeSuccessPopup">닫기</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// 폼 데이터
const formData = ref({
    email: '',
    password: '',
    confirmPassword: '',
    nickname: '',
    birthdate: ''
})

// 상태 관리
const errors = ref({})
const agreeTerms = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isSubmitting = ref(false)
const isCheckingEmail = ref(false)
const emailCheckResult = ref('')
const showSuccessPopup = ref(false)
const showTermsModal = ref(false)
const showPrivacyModal = ref(false)

const agreeToTerms = () => {
    agreeTerms.value = true
    showTermsModal.value = false
    clearError('terms')
}

const agreeToPrivacy = () => {
    agreeTerms.value = true
    showPrivacyModal.value = false
    clearError('terms')
}

// 이메일 유효성 검사
const isEmailValid = computed(() => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(formData.value.email)
})

// 폼 전체 유효성 검사
const isFormValid = computed(() => {
    return isEmailValid.value &&
        formData.value.password.length >= 8 &&
        formData.value.password === formData.value.confirmPassword &&
        formData.value.nickname.length >= 2 &&
        formData.value.birthdate &&
        agreeTerms.value &&
        emailCheckResult.value &&
        Object.keys(errors.value).length === 0
})

// 에러 클리어
const clearError = (field) => {
    if (errors.value[field]) {
        delete errors.value[field]
    }
}

// 이메일 유효성 검사
const validateEmail = () => {
    if (!formData.value.email) {
        errors.value.email = '이메일을 입력해주세요'
    } else if (!isEmailValid.value) {
        errors.value.email = '올바른 이메일 형식이 아닙니다'
    } else {
        clearError('email')
    }
}

// 이메일 중복 확인
const checkEmailDuplicate = async () => {
    if (!isEmailValid.value) return

    isCheckingEmail.value = true
    emailCheckResult.value = ''

    try {
        // 실제 API 호출 시뮬레이션
        await new Promise(resolve => setTimeout(resolve, 1000))

        // 여기서 실제 API를 호출하세요
        const isDuplicate = Math.random() > 0.7 // 30% 확률로 중복

        if (isDuplicate) {
            errors.value.email = '이미 사용 중인 이메일입니다'
            emailCheckResult.value = ''
        } else {
            clearError('email')
            emailCheckResult.value = '사용 가능한 이메일입니다'
        }
    } catch (error) {
        errors.value.email = '이메일 확인 중 오류가 발생했습니다'
    } finally {
        isCheckingEmail.value = false
    }
}

// 비밀번호 강도 계산
const getPasswordStrength = () => {
    const password = formData.value.password
    let strength = 0

    if (password.length >= 8) strength++
    if (/[a-z]/.test(password)) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/[0-9]/.test(password)) strength++
    if (/[^A-Za-z0-9]/.test(password)) strength++

    return Math.min(strength, 4)
}

const getPasswordStrengthText = () => {
    const strength = getPasswordStrength()
    const texts = ['매우 약함', '약함', '보통', '강함', '매우 강함']
    return texts[strength] || '매우 약함'
}

const getPasswordStrengthClass = () => {
    const strength = getPasswordStrength()
    const classes = ['very-weak', 'weak', 'medium', 'strong', 'very-strong']
    return classes[strength] || 'very-weak'
}

// 비밀번호 유효성 검사
const validatePassword = () => {
    if (!formData.value.password) {
        errors.value.password = '비밀번호를 입력해주세요'
    } else if (formData.value.password.length < 8) {
        errors.value.password = '비밀번호는 8자 이상이어야 합니다'
    } else {
        clearError('password')
    }
}

// 비밀번호 확인 검사
const validateConfirmPassword = () => {
    if (!formData.value.confirmPassword) {
        errors.value.confirmPassword = '비밀번호 확인을 입력해주세요'
    } else if (formData.value.password !== formData.value.confirmPassword) {
        errors.value.confirmPassword = '비밀번호가 일치하지 않습니다'
    } else {
        clearError('confirmPassword')
    }
}

// 닉네임 유효성 검사
const validateNickname = () => {
    if (!formData.value.nickname) {
        errors.value.nickname = '닉네임을 입력해주세요'
    } else if (formData.value.nickname.length < 2) {
        errors.value.nickname = '닉네임은 2자 이상이어야 합니다'
    } else if (formData.value.nickname.length > 20) {
        errors.value.nickname = '닉네임은 20자 이하여야 합니다'
    } else {
        clearError('nickname')
    }
}

// 생년월일 유효성 검사
const validateBirthdate = () => {
    if (!formData.value.birthdate) {
        errors.value.birthdate = '생년월일을 입력해주세요'
    } else {
        const birthDate = new Date(formData.value.birthdate)
        const today = new Date()
        const age = today.getFullYear() - birthDate.getFullYear()

        if (age < 14) {
            errors.value.birthdate = '14세 이상만 가입 가능합니다'
        } else if (age > 120) {
            errors.value.birthdate = '올바른 생년월일을 입력해주세요'
        } else {
            clearError('birthdate')
        }
    }
}

// 폼 제출
const handleSubmit = async () => {
    // 모든 필드 유효성 검사
    validateEmail()
    validatePassword()
    validateConfirmPassword()
    validateNickname()
    validateBirthdate()

    if (!agreeTerms.value) {
        errors.value.terms = '약관에 동의해주세요'
    }

    if (!isFormValid.value) return

    isSubmitting.value = true

    try {
        // 실제 API 호출 시뮬레이션
        await new Promise(resolve => setTimeout(resolve, 2000))

        // 여기서 실제 회원가입 API를 호출하세요
        console.log('회원가입 데이터:', {
            email: formData.value.email,
            password: formData.value.password,
            nickname: formData.value.nickname,
            birthdate: formData.value.birthdate
        })

        // 성공 팝업 표시
        showSuccessPopup.value = true

    } catch (error) {
        console.error('회원가입 실패:', error)
        // 에러 처리
    } finally {
        isSubmitting.value = false
    }
}

// 성공 팝업 닫기
const closeSuccessPopup = () => {
    showSuccessPopup.value = false
}

// 로그인 페이지로 이동
const goToLogin = () => {
    closeSuccessPopup()
    // 여기서 로그인 페이지로 라우팅
    console.log('로그인 페이지로 이동')
}

// 이메일 변경 시 중복확인 결과 초기화
watch(() => formData.value.email, () => {
    emailCheckResult.value = ''
})
</script>

<style scoped>
.signup-page {
    min-height: 100vh;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
    overflow: hidden;
}

.background-gradient {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg,
            #0a0a0a 0%,
            #1a0f1f 20%,
            #2d1b69 40%,
            #8e2de2 60%,
            #4a00e0 80%,
            #000000 100%);
    z-index: -2;
}

.background-gradient::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 30% 20%, rgba(138, 43, 226, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 70% 80%, rgba(74, 0, 224, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 20% 80%, rgba(142, 45, 226, 0.2) 0%, transparent 50%);
    animation: gradientShift 8s ease-in-out infinite alternate;
}

@keyframes gradientShift {
    0% {
        opacity: 0.7;
    }

    100% {
        opacity: 1;
    }
}

.signup-container {
    width: 100%;
    max-width: 500px;
    z-index: 1;
    position: relative;
}

.signup-card {
    background: rgba(0, 0, 0, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    backdrop-filter: blur(20px);
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(255, 255, 255, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.signup-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(138, 43, 226, 0.8) 50%,
            transparent 100%);
}

.signup-header {
    text-align: center;
    margin-bottom: 2.5rem;
}

.signup-title {
    color: #ffffff;
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #ffffff 0%, #e8e8e8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: 0 2px 10px rgba(255, 255, 255, 0.1);
}

.signup-subtitle {
    color: rgba(255, 255, 255, 0.75);
    font-size: 1.05rem;
    margin: 0;
    font-weight: 400;
}

.signup-form {
    display: flex;
    flex-direction: column;
    gap: 1.8rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    position: relative;
}

.form-label {
    color: #ffffff;
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 0.7rem;
    letter-spacing: 0.5px;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.form-input {
    width: 100%;
    padding: 1rem 1.2rem;
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 400;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}

.form-input::placeholder {
    color: rgba(255, 255, 255, 0.45);
    transition: all 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: rgba(205, 43, 226, 0.8);
    background: rgba(255, 255, 255, 0.12);
    box-shadow:
        0 0 0 0.3rem rgba(138, 43, 226, 0.15),
        0 8px 25px rgba(138, 43, 226, 0.1);
    transform: translateY(-1px);
}

.form-input:focus::placeholder {
    color: rgba(255, 255, 255, 0.6);
    transform: translateX(4px);
}

.form-input.error {
    border-color: rgba(255, 99, 132, 0.8);
    background: rgba(255, 99, 132, 0.08);
    box-shadow: 0 0 0 0.2rem rgba(255, 99, 132, 0.15);
}

.form-input.success {
    border-color: rgba(75, 192, 182, 0.8);
    background: rgba(75, 192, 192, 0.08);
    box-shadow: 0 0 0 0.2rem rgba(75, 192, 192, 0.15);
}

.check-duplicate-btn {
    position: absolute;
    right: 0.8rem;
    background: linear-gradient(135deg, rgba(104, 24, 30, 0.9), rgba(85, 16, 223, 0.9));
    border: none;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
}

.check-duplicate-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, rgba(204, 0, 0), rgba(88, 0, 255));
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 25px rgba(138, 43, 226, 0.4);
}

.check-duplicate-btn:disabled {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.4);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.toggle-password-btn {
    position: absolute;
    right: 1rem;
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.6);
    padding: 0.5rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1.1rem;
}

.toggle-password-btn:hover {
    color: rgba(255, 255, 255, 0.9);
    background: rgba(255, 255, 255, 0.1);
    transform: scale(1.1);
}

.error-message {
    color: rgba(255, 99, 132, 0.9);
    font-size: 0.85rem;
    margin-top: 0.5rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.error-message::before {
    content: '⚠';
    font-size: 0.9rem;
}

.success-message {
    color: rgba(75, 192, 192, 0.9);
    font-size: 0.85rem;
    margin-top: 0.5rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.success-message::before {
    content: '✓';
    font-size: 0.9rem;
}

/* 비밀번호 강도 표시기 */
.password-strength {
    margin-top: 0.8rem;
}

.strength-bar {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
    overflow: hidden;
    position: relative;
}

.strength-fill {
    height: 100%;
    transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    border-radius: 3px;
    position: relative;
    overflow: hidden;
}

.strength-fill::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: shimmer 2s infinite;
}

@keyframes shimmer {
    0% {
        left: -100%;
    }

    100% {
        left: 100%;
    }
}

.strength-fill.very-weak {
    background: linear-gradient(90deg, #ff4757, #ff6b7a);
}

.strength-fill.weak {
    background: linear-gradient(90deg, #ff7675, #fd79a8);
}

.strength-fill.medium {
    background: linear-gradient(90deg, #fdcb6e, #e17055);
}

.strength-fill.strong {
    background: linear-gradient(90deg, #6c5ce7, #a29bfe);
}

.strength-fill.very-strong {
    background: linear-gradient(90deg, #00b894, #2ed573);
}

.strength-text {
    font-size: 0.8rem;
    margin-top: 0.5rem;
    margin-bottom: 0;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.strength-text.very-weak {
    color: #ff4757;
}

.strength-text.weak {
    color: #ff7675;
}

.strength-text.medium {
    color: #fdcb6e;
}

.strength-text.strong {
    color: #6c5ce7;
}

.strength-text.very-strong {
    color: #2ed573;
}

/* 약관 동의 */
.terms-section {
    margin: 1rem 0;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.checkbox-group {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
}

.checkbox-input {
    display: none;
}

.checkbox-label {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    cursor: pointer;
    line-height: 1.5;
    transition: all 0.3s ease;
}

.checkbox-label:hover {
    transform: translateX(2px);
}

.checkbox-custom {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    background: transparent;
    position: relative;
    flex-shrink: 0;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.checkbox-input:checked+.checkbox-label .checkbox-custom {
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
    border-color: transparent;
    transform: scale(1.1);
}

.checkbox-input:checked+.checkbox-label .checkbox-custom::after {
    content: '✓';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) scale(1.2);
    color: white;
    font-size: 12px;
    font-weight: bold;
    animation: checkmark 0.3s ease-in-out;
}

@keyframes checkmark {
    0% {
        transform: translate(-50%, -50%) scale(0) rotate(45deg);
    }

    100% {
        transform: translate(-50%, -50%) scale(1.2) rotate(0deg);
    }
}

.checkbox-text {
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.95rem;
    font-weight: 400;
}

.terms-link {
    color: #8e2de2;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    position: relative;
}

.terms-link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
    transition: width 0.3s ease;
}

.terms-link:hover {
    color: #4a00e0;
}

.terms-link:hover::after {
    width: 100%;
}

/* 회원가입 버튼 */
.signup-btn {
    width: 100%;
    padding: 1.2rem;
    background: linear-gradient(135deg, #8e2de2 0%, #4a00e0 100%);
    border: none;
    color: white;
    font-size: 1.1rem;
    font-weight: 700;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    margin-top: 1.5rem;
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.signup-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

.signup-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #a653e8 0%, #5d15e6 100%);
    transform: translateY(-3px);
    box-shadow:
        0 15px 40px rgba(138, 43, 226, 0.4),
        0 0 0 1px rgba(255, 255, 255, 0.1);
}

.signup-btn:hover:not(:disabled)::before {
    left: 100%;
}

.signup-btn:active:not(:disabled) {
    transform: translateY(-1px);
}

.signup-btn:disabled {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.4);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
}

.loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

/* 로그인 링크 */
.login-link {
    text-align: center;
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
}

.login-link::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 50px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(138, 43, 226, 0.8), transparent);
}

.login-link p {
    color: rgba(255, 255, 255, 0.75);
    margin: 0;
    font-size: 0.95rem;
}

.link {
    color: #8e2de2;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    position: relative;
}

.link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
    transition: width 0.3s ease;
}

.link:hover {
    color: #4a00e0;
}

.link:hover::after {
    width: 100%;
}

/* 성공 팝업 */
.popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(15px);
    animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}

.popup-content {
    background: rgba(0, 0, 0, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    padding: 3rem 2.5rem;
    max-width: 450px;
    width: 90%;
    text-align: center;
    backdrop-filter: blur(30px);
    box-shadow:
        0 30px 80px rgba(0, 0, 0, 0.6),
        0 0 0 1px rgba(255, 255, 255, 0.05);
    position: relative;
    animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(50px) scale(0.9);
    }

    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.popup-content::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(138, 43, 226, 0.8) 50%,
            transparent 100%);
    border-radius: 20px 20px 0 0;
}

.popup-header {
    margin-bottom: 2.5rem;
}

.success-icon {
    font-size: 5rem;
    color: rgba(100, 226, 183);
    margin-bottom: 1.5rem;
    animation: bounce 0.6s ease-out;
}

@keyframes bounce {
    0% {
        transform: scale(0);
    }

    50% {
        transform: scale(1.2);
    }

    100% {
        transform: scale(1);
    }
}

.popup-title {
    color: #ffffff;
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #ffffff 0%, #e8e8e8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.popup-message {
    color: rgba(255, 255, 255, 0.85);
    line-height: 1.6;
    margin: 0;
    font-size: 1.05rem;
}

.popup-actions {
    display: flex;
    gap: 1.2rem;
    justify-content: center;
    flex-wrap: wrap;
}

.popup-btn {
    padding: 0.9rem 2rem;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-width: 120px;
}

.popup-btn.primary {
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
    color: white;
}

.popup-btn.primary::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

.popup-btn.primary:hover {
    background: linear-gradient(135deg, #a653e8, #5d15e6);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(138, 43, 226, 0.4);
}

.popup-btn.primary:hover::before {
    left: 100%;
}

.popup-btn.secondary {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.popup-btn.secondary:hover {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
    .signup-page {
        padding: 1.5rem 1rem;
    }

    .signup-card {
        padding: 2.5rem 2rem;
        border-radius: 16px;
    }

    .signup-title {
        font-size: 1.9rem;
    }

    .form-input {
        padding: 0.9rem 1rem;
    }

    .popup-content {
        padding: 2.5rem 2rem;
        border-radius: 16px;
    }

    .popup-actions {
        flex-direction: column;
        align-items: center;
    }

    .popup-btn {
        width: 100%;
        max-width: 200px;
    }
}

@media (max-width: 480px) {
    .signup-page {
        padding: 1rem 0.5rem;
    }

    .signup-card {
        padding: 2rem 1.5rem;
        border-radius: 12px;
    }

    .signup-title {
        font-size: 1.6rem;
    }

    .form-input {
        font-size: 16px;
        /* iOS 줌 방지 */
        padding: 0.8rem 1rem;
    }

    .popup-content {
        padding: 2rem 1.5rem;
    }

    .success-icon {
        font-size: 4rem;
    }

    .popup-title {
        font-size: 1.5rem;
    }
}

/* 다크모드 최적화 */
@media (prefers-color-scheme: dark) {
    .signup-card {
        background: rgba(0, 0, 0, 0.9);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .form-input {
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.2);
    }

    .terms-section {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.15);
    }
}

/* 접근성 개선 */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* 포커스 스타일 */
.form-input:focus-visible,
.signup-btn:focus-visible,
.popup-btn:focus-visible {
    outline: 2px solid rgba(138, 43, 226, 0.8);
    outline-offset: 2px;
}

.checkbox-input:focus-visible+.checkbox-label .checkbox-custom {
    outline: 2px solid rgba(138, 43, 226, 0.8);
    outline-offset: 2px;
    border-radius: 6px;
}

/* 이용약관 모달 스타일 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    backdrop-filter: blur(15px);
    animation: fadeIn 0.3s ease-out;
    padding: 2rem 1rem;
}

.modal-content {
    background: rgba(0, 0, 0, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(30px);
    box-shadow:
        0 30px 80px rgba(0, 0, 0, 0.6),
        0 0 0 1px rgba(255, 255, 255, 0.05);
    position: relative;
    animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.modal-content::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(138, 43, 226, 0.8) 50%,
            transparent 100%);
    border-radius: 20px 20px 0 0;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 2.5rem 1rem 2.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    flex-shrink: 0;
}

.modal-title {
    color: #ffffff;
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, #e8e8e8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.modal-close-btn {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: rgba(255, 255, 255, 0.7);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1.2rem;
}

.modal-close-btn:hover {
    background: rgba(255, 99, 132, 0.2);
    color: rgba(255, 99, 132, 0.9);
    transform: scale(1.1);
}

.modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 0 2.5rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(138, 43, 226, 0.5) rgba(255, 255, 255, 0.1);
}

.modal-body::-webkit-scrollbar {
    width: 8px;
}

.modal-body::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.6), rgba(74, 0, 224, 0.6));
    border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.8), rgba(74, 0, 224, 0.8));
}

.terms-content {
    padding: 1.5rem 0;
    line-height: 1.7;
}

.terms-content h3 {
    color: #ffffff;
    font-size: 1.2rem;
    font-weight: 600;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(138, 43, 226, 0.3);
    position: relative;
}

.terms-content h3::before {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 50px;
    height: 2px;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
}

.terms-content h3:first-child {
    margin-top: 0;
}

.terms-content p {
    color: rgba(255, 255, 255, 0.85);
    margin: 1rem 0;
    font-size: 0.95rem;
}

.terms-content ul {
    margin: 1rem 0;
    padding-left: 1.5rem;
}

.terms-content li {
    color: rgba(255, 255, 255, 0.8);
    margin: 0.5rem 0;
    font-size: 0.9rem;
    position: relative;
}

.terms-content li::marker {
    color: rgba(138, 43, 226, 0.7);
}

.terms-content strong {
    color: rgba(255, 255, 255, 0.95);
    font-weight: 600;
}

.terms-date {
    background: rgba(138, 43, 226, 0.1);
    border: 1px solid rgba(138, 43, 226, 0.3);
    border-radius: 8px;
    padding: 1rem;
    margin: 2rem 0 0 0;
    text-align: center;
}

.terms-date strong {
    color: #ffffff;
}

/* 이용약관 모달 스타일 */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.9);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    backdrop-filter: blur(15px);
    animation: fadeIn 0.3s ease-out;
    padding: 2rem 1rem;
}

.modal-content {
    background: rgba(0, 0, 0, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    backdrop-filter: blur(30px);
    box-shadow:
        0 30px 80px rgba(0, 0, 0, 0.6),
        0 0 0 1px rgba(255, 255, 255, 0.05);
    position: relative;
    animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.modal-content::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg,
            transparent 0%,
            rgba(138, 43, 226, 0.8) 50%,
            transparent 100%);
    border-radius: 20px 20px 0 0;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2rem 2.5rem 1rem 2.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    flex-shrink: 0;
}

.modal-title {
    color: #ffffff;
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, #e8e8e8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.modal-close-btn {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: rgba(255, 255, 255, 0.7);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1.2rem;
}

.modal-close-btn:hover {
    background: rgba(255, 99, 132, 0.2);
    color: rgba(255, 99, 132, 0.9);
    transform: scale(1.1);
}

.modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 0 2.5rem;
    scrollbar-width: thin;
    scrollbar-color: rgba(138, 43, 226, 0.5) rgba(255, 255, 255, 0.1);
}

.modal-body::-webkit-scrollbar {
    width: 8px;
}

.modal-body::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.6), rgba(74, 0, 224, 0.6));
    border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.8), rgba(74, 0, 224, 0.8));
}

.terms-content {
    padding: 1.5rem 0;
    line-height: 1.7;
}

.terms-content h3 {
    color: #ffffff;
    font-size: 1.2rem;
    font-weight: 600;
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid rgba(138, 43, 226, 0.3);
    position: relative;
}

.terms-content h3::before {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 50px;
    height: 2px;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
}

.terms-content h3:first-child {
    margin-top: 0;
}

.terms-content p {
    color: rgba(255, 255, 255, 0.85);
    margin: 1rem 0;
    font-size: 0.95rem;
}

.terms-content ul {
    margin: 1rem 0;
    padding-left: 1.5rem;
}

.terms-content li {
    color: rgba(255, 255, 255, 0.8);
    margin: 0.5rem 0;
    font-size: 0.9rem;
    position: relative;
}

.terms-content li::marker {
    color: rgba(138, 43, 226, 0.7);
}

.terms-content strong {
    color: rgba(255, 255, 255, 0.95);
    font-weight: 600;
}

.terms-date {
    background: rgba(138, 43, 226, 0.1);
    border: 1px solid rgba(138, 43, 226, 0.3);
    border-radius: 8px;
    padding: 1rem;
    margin: 2rem 0 0 0;
    text-align: center;
}

.terms-date strong {
    color: #ffffff;
    font-size: 1rem;
}

.modal-footer {
    padding: 1.5rem 2.5rem 2rem 2.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    flex-shrink: 0;
}

.modal-btn {
    padding: 0.8rem 1.8rem;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-width: 100px;
}

.modal-btn.primary {
    background: linear-gradient(135deg, #8e2de2, #4a00e0);
    color: white;
}

.modal-btn.primary::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

.modal-btn.primary:hover {
    background: linear-gradient(135deg, #a653e8, #5d15e6);
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(138, 43, 226, 0.4);
}

.modal-btn.primary:hover::before {
    left: 100%;
}

.modal-btn.secondary {
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-btn.secondary:hover {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

/* 반응형 모달 */
@media (max-width: 768px) {
    .modal-overlay {
        padding: 1rem 0.5rem;
    }

    .modal-content {
        border-radius: 16px;
        max-height: 95vh;
    }

    .modal-header {
        padding: 1.5rem 1.5rem 1rem 1.5rem;
    }

    .modal-title {
        font-size: 1.3rem;
    }

    .modal-body {
        padding: 0 1.5rem;
    }

    .terms-content {
        padding: 1rem 0;
    }

    .terms-content h3 {
        font-size: 1.1rem;
    }

    .modal-footer {
        padding: 1rem 1.5rem 1.5rem 1.5rem;
        flex-direction: column;
    }

    .modal-btn {
        width: 100%;
        padding: 1rem;
    }
}

@media (max-width: 480px) {
    .modal-overlay {
        padding: 0.5rem;
    }

    .modal-content {
        border-radius: 12px;
        max-height: 98vh;
    }

    .modal-header {
        padding: 1rem;
    }

    .modal-title {
        font-size: 1.2rem;
    }

    .modal-body {
        padding: 0 1rem;
    }

    .terms-content {
        padding: 0.5rem 0;
    }

    .terms-content h3 {
        font-size: 1rem;
        margin: 1.5rem 0 0.8rem 0;
    }

    .terms-content p,
    .terms-content li {
        font-size: 0.85rem;
    }

    .modal-footer {
        padding: 1rem;
    }
}

/* 키보드 접근성 */
.modal-content:focus-within {
    outline: 2px solid rgba(138, 43, 226, 0.5);
    outline-offset: -2px;
}

.modal-close-btn:focus-visible,
.modal-btn:focus-visible {
    outline: 2px solid rgba(138, 43, 226, 0.8);
    outline-offset: 2px;
}

/* 다크모드 최적화 */
@media (prefers-color-scheme: dark) {
    .modal-content {
        background: rgba(0, 0, 0, 0.98);
        border-color: rgba(255, 255, 255, 0.25);
    }

    .terms-content {
        color: rgba(255, 255, 255, 0.9);
    }
}
</style>