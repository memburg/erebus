classdef Erebus
    methods (Static, Access = private)
        function createKey(x, y, iterations)
            % Create a Mx3 matrix, full of zeros.
            key = zeros(iterations, 3);

            % Assign random numbers between 0 and 1,
            % in which 0 represents a row, and 1
            % represents a column.
            key(:, 1) = randi([0 1], iterations, 1);

            % 0 - rows
            % 1 - columns
            for i = 1:iterations
                switch key(i, 1)
                    case 0
                        randRow = randi([1 x], iterations, 1);
                        randMvmts = randi([-x x], iterations, 1);
                        key(i, 2) = randRow(1, 1);
                        key(i, 3) = randMvmts(1, 1);
                    case 1
                        randColumn = randi([1 y], iterations, 1);
                        randMvmts = randi([-y y], iterations, 1);
                        key(i, 2) = randColumn(1, 1);
                        key(i, 3) = randMvmts(1, 1);
                    otherwise
                        error("Unexpeceted error while creating encryption key");
                end
            end

            date = datestr(now,'yy_mm_dd_HH_MM_SS');
            writematrix(key, "./outputs/" + date + ".csv");
        end
    end

    methods (Static)
        function protect()
            tic;
            Erebus.createKey(2, 100, 800);
            toc;
        end
    end
end
