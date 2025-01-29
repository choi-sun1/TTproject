document.addEventListener('DOMContentLoaded', function() {
    // wizardData 초기화
    let wizardData = {...wizardDataStructure};
    
    // 이전 데이터가 있다면 로드
    const savedData = wizardStorage.load();
    if (savedData) {
        wizardData = {...wizardData, ...savedData};
        initializeFormFields(wizardData);
    }
    
    // 날짜 입력 이벤트 리스너
    document.getElementById('start_date').addEventListener('change', validateDates);
    document.getElementById('end_date').addEventListener('change', validateDates);
    
    // 폼 제출 핸들러
    document.getElementById('basicForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted'); // 디버깅용
        
        try {
            showLoadingSpinner();
            
            // 폼 데이터 수집 - 필드명을 HTML과 일치시킴
            const formData = {
                title: document.getElementById('title').value.trim(),
                destination: document.getElementById('destination').value.trim(),
                start_date: document.getElementById('start_date').value,
                end_date: document.getElementById('end_date').value,
                styles: Array.from(document.querySelectorAll('input[name="styles[]"]:checked'))
                        .map(cb => cb.value)
            };
            
            console.log('Form data:', formData); // 디버깅용
            
            // 데이터 검증 - styles 유효성 검사 제거
            if (!formData.title?.trim()) {
                showError('여행 제목을 입력해주세요.');
                return;
            }
            if (!formData.destination?.trim()) {
                showError('여행지를 입력해주세요.');
                return;
            }
            if (!formData.start_date || !formData.end_date) {
                showError('여행 날짜를 선택해주세요.');
                return;
            }
            if (!validateDates()) {
                return;
            }
            // styles는 선택사항으로 변경
            
            // wizardData 업데이트 및 저장 - 필드명 일치
            const wizardData = {
                ...wizardDataStructure,
                ...formData
            };
            console.log('Saving wizard data:', wizardData); // 디버깅용
            wizardStorage.save(wizardData);
            
            // 서버로 전송
            const response = await fetch('/itineraries/wizard/step1/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                credentials: 'same-origin',
                body: JSON.stringify(formData)
            });
            
            console.log('Server response:', response); // 디버깅용
            
            if (!response.ok) {
                throw new Error(`서버 오류: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Response data:', data); // 디버깅용
            
            if (data.status === 'success') {
                window.location.href = '/itineraries/wizard/step2/';
            } else {
                throw new Error(data.message || '저장에 실패했습니다.');
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            showError(error.message);
        } finally {
            hideLoadingSpinner();
        }
    });
    
    // 폼 데이터 유효성 검사 수정
    function validateFormData(data) {
        if (!data.title?.trim()) {
            showError('여행 제목을 입력해주세요.');
            return false;
        }
        if (!data.destination?.trim()) {
            showError('여행지를 입력해주세요.');
            return false;
        }
        if (!data.start_date || !data.end_date) {  // 필드명 수정
            showError('여행 날짜를 선택해주세요.');
            return false;
        }
        if (!validateDates()) {
            return false;
        }
        return true;
    }
});

// 폼 필드 초기화
function initializeFormFields(data) {
    if (data.title) document.getElementById('title').value = data.title;
    if (data.destination) document.getElementById('destination').value = data.destination;
    if (data.startDate) document.getElementById('start_date').value = data.startDate;
    if (data.endDate) document.getElementById('end_date').value = data.endDate;
    if (data.styles) {
        data.styles.forEach(style => {
            const checkbox = document.querySelector(`input[name="styles[]"][value="${style}"]`);
            if (checkbox) checkbox.checked = true;
        });
    }
}

// 날짜 유효성 검사
function validateDates() {
    const startDate = new Date(document.getElementById('start_date').value);
    const endDate = new Date(document.getElementById('end_date').value);
    
    if (endDate < startDate) {
        showError('종료일은 시작일보다 이후여야 합니다.');
        document.getElementById('end_date').value = '';
        return false;
    }
    return true;
}
