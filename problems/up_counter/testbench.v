module upcounter_testbench();
    reg clk, reset;
    wire [3:0] counter;

    // 實例化待測模組
    up_counter dut(clk, reset, counter);

    // 產生時鐘信號
    initial begin
        clk = 0;
        forever #5 clk = ~clk;  // 每 5 時間單位翻轉一次時鐘
    end

    // 產生重置信號
    initial begin
        reset = 1;  // 初始化時重置
        #20;        // 維持 20 時間單位
        reset = 0;  // 解除重置
    end

    // 驗證計數器行為
    initial begin
        #25;  // 等待重置完成後的第一個時鐘週期
        if (counter != 0) begin
            $display("Test failed at time %0t: Counter is not 0 after reset, value = %d", $time, counter);
            $finish;
        end

        // 驗證計數器是否正確遞增
        repeat (16) begin
            #10;  // 每個完整時鐘週期檢查一次
            if (counter !== (($time - 25) / 10) % 16) begin
                $display("Test failed at time %0t: Counter value = %d, expected = %d", 
                         $time, counter, (($time - 25) / 10) % 16);
                $finish;
            end
        end

        // 如果通過所有測試，打印成功信息
        $display("Test passed");
        $finish;
    end
endmodule