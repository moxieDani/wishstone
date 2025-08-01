<script>
  import ct from 'countries-and-timezones';
  
  let userInput = '';
  let isProcessing = false;

  // IP 주소 가져오기
  async function fetchIPAddress() {
    try {
      const response = await fetch("https://ifconfig.me/ip");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const ip = (await response.text()).trim();
      return ip;
    } catch (error) {
      console.error("클라이언트 IP 주소를 가져오는 데 실패했습니다:", error);
      return "알 수 없음";
    }
  }

  // 새로 추가된 fetchTimezoneFull 함수
  async function fetchTimezoneFull() {
    try {
      const iana = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const now = new Date();
      const offsetMin = -now.getTimezoneOffset();
      const sign = offsetMin >= 0 ? '+' : '-';
      const abs = Math.abs(offsetMin);
      const h = String(Math.floor(abs / 60)).padStart(2, '0');
      const m = String(abs % 60).padStart(2, '0');
      const utcOffsetStd = `${sign}${h}:${m}`;

      // user locale time formatted
      const pad2 = n => String(n).padStart(2, '0');
      const localDate = `${now.getFullYear()}-${pad2(now.getMonth()+1)}-${pad2(now.getDate())}`;
      const localTime = `${pad2(now.getHours())}:${pad2(now.getMinutes())}:${pad2(now.getSeconds())}`;
      const timestamp_with_timezone = `${localDate} ${localTime}${utcOffsetStd}`;

      const utc = `${now.getUTCFullYear()}-${pad2(now.getUTCMonth()+1)}-${pad2(now.getUTCDate())} ` +
                  `${pad2(now.getUTCHours())}:${pad2(now.getUTCMinutes())}:${pad2(now.getUTCSeconds())}`;

      // country name lookup
      const country = ct.getCountryForTimezone(iana);
      const country_name = country?.name || null;

      return {
        timestamp_with_timezone,
        utc,
        timezone_name: iana,
        country_name
      };
    } catch (error) {
      console.error('fetchTimezoneFull 오류:', error);
      return {
        timestamp_with_timezone: '알 수 없음',
        utc: '알 수 없음',
        timezone_name: '알 수 없음',
        country_name: null
      };
    }
  }

  // 모든 정보를 수집하고 백엔드로 전송
  async function processAllInfo() {
    if (!userInput.trim()) {
      alert('텍스트를 입력해주세요!');
      return;
    }

    isProcessing = true;

    try {
      // IP 주소와 국가 정보 가져오기
      const [ipAddress, timezoneFull] = await Promise.all([
        fetchIPAddress(),
        fetchTimezoneFull()  // 새로 추가된 함수 사용
      ]);

      const requestData = {
        text: userInput,
        ip_address: ipAddress,
        timezone: timezoneFull?.timezone_name || '알 수 없음',
        current_time: timezoneFull?.timestamp_with_timezone || '알 수 없음',
        utc_time: timezoneFull?.utc || '알 수 없음',
        country_name: timezoneFull?.country_name || '알 수 없음',
        // 새로 추가된 데이터
        timezone_full: timezoneFull
      };

      // 백엔드 API 호출
      const response = await fetch('http://localhost:5847/api/process-all', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      const result = await response.json();

      if (result.success) {
        alert('✅ 성공: ' + result.message);
      } else {
        alert('❌ 실패: ' + result.message);
      }

    } catch (error) {
      console.error('처리 중 오류 발생:', error);
      alert('❌ 실패: 서버와의 통신에 실패했습니다.');
    } finally {
      isProcessing = false;
    }
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      processAllInfo();
    }
  }
</script>

<div class="container">
  <h1>WishStone</h1>
    <div class="input-group">
      <input 
        type="text" 
        bind:value={userInput} 
        on:keypress={handleKeyPress}
        placeholder="소원을 입력하세요." 
        disabled={isProcessing}
      />
      <button 
        on:click={processAllInfo} 
        disabled={isProcessing || !userInput.trim()}
      >
        {isProcessing ? '처리 중...' : '정보 전송'}
      </button>
  </div>
</div>

<style>
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 30px;
    background: #4facfe;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }
  
  .input-group {
    display: flex;
    gap: 10px;
    background: white;
    align-items: center;
    margin-top: 15px;
  }

  .input-group input {
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 5px;
    font-size: 16px;
  }

  .input-group button {
    padding: 10px 20px;
    background: #ff6b6b;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.3s;
  }

  .input-group button:hover:not(:disabled) {
    background: #ff5252;
  }

  .input-group button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  h1 {
    text-align: center;
    color: #333;
    margin-bottom: 30px;
  }
</style>