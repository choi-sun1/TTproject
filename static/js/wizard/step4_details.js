document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('detailsForm');
    const checklistContainer = document.getElementById('checklistContainer');
    
    // 기본 체크리스트 아이템 초기화
    initializeChecklist();
    
    // 예산 입력 이벤트 리스너
    document.querySelectorAll('.budget-input input').forEach(input => {
        input.addEventListener('input', calculateTotalBudget);
    });
    
    // 폼 제출 이벤트
    form.addEventListener('submit', handleSubmit);
});

// 기본 체크리스트 초기화
function initializeChecklist() {
    const defaultItems = [
        { text: '여권/신분증', checked: false },
        { text: '숙소 예약 확인서', checked: false },
        { text: '항공권', checked: false },
        { text: '여행자 보험', checked: false },
        { text: '필수 약품', checked: false }
    ];
    
    defaultItems.forEach(item => addChecklistItem(item));
}

// 체크리스트 아이템 추가
function addChecklistItem(item = { text: '', checked: false }) {
    const itemDiv = document.createElement('div');
    itemDiv.className = 'checklist-item';
    itemDiv.innerHTML = `
        <div class="drag-handle">
            <i class="fas fa-grip-vertical"></i>
        </div>
        <input type="checkbox" ${item.checked ? 'checked' : ''}>
        <input type="text" value="${item.text}" placeholder="준비물을 입력하세요">
        <button type="button" class="remove-btn" onclick="removeChecklistItem(this)">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    checklistContainer.appendChild(itemDiv);
    initializeDragAndDrop();
}

// 체크리스트 아이템 삭제
function removeChecklistItem(button) {
    button.closest('.checklist-item').remove();
}

// 예산 총액 계산
function calculateTotalBudget() {
    let total = 0;
    document.querySelectorAll('.budget-input input').forEach(input => {
        const value = parseInt(input.value) || 0;
        total += value;
    });
    
    document.getElementById('totalBudget').textContent = 
        total.toLocaleString() + '원';
}

// 드래그 앤 드롭 초기화
function initializeDragAndDrop() {
    new Sortable(checklistContainer, {
        animation: 150,
        handle: '.drag-handle',
        ghostClass: 'checklist-item-ghost'
    });
}

// 폼 제출 처리
async function handleSubmit(e) {
    e.preventDefault();
    
    try {
        showLoadingSpinner();
        
        // 데이터 수집
        const formData = {
            budgets: collectBudgetData(),
            checklist: collectChecklistData(),
            is_public: document.querySelector('[name="is_public"]').checked,
            notes: document.querySelector('[name="notes"]').value
        };
        
        // 기존 wizard 데이터와 병합
        const wizardData = JSON.parse(sessionStorage.getItem('wizard_data') || '{}');
        Object.assign(wizardData, formData);
        
        // 서버로 전송
        const response = await fetch('/itineraries/wizard/step4/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        if (data.success) {
            // 세션 스토리지 초기화
            sessionStorage.removeItem('wizard_data');
            
            // 완료 페이지로 이동
            window.location.href = data.redirect_url;
        } else {
            throw new Error(data.error || '저장에 실패했습니다.');
        }
    } catch (error) {
        console.error('Submit error:', error);
        showError(error.message);
    } finally {
        hideLoadingSpinner();
    }
}

// 예산 데이터 수집
function collectBudgetData() {
    const budgets = {};
    document.querySelectorAll('.budget-input input').forEach(input => {
        const category = input.name.replace('budget_', '');
        const amount = parseInt(input.value) || 0;
        if (amount > 0) {
            budgets[category] = amount;
        }
    });
    return budgets;
}

// 체크리스트 데이터 수집
function collectChecklistData() {
    return Array.from(document.querySelectorAll('.checklist-item')).map(item => ({
        text: item.querySelector('input[type="text"]').value,
        checked: item.querySelector('input[type="checkbox"]').checked
    })).filter(item => item.text.trim());
}
