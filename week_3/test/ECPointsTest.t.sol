// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

import {Test, console} from "forge-std/Test.sol";
import {ECPoints} from "../src/ECPoints.sol";
import {HelperConfig} from "../script/HelperConfig.s.sol";

contract ECPointsTest is Test {
    ECPoints public numbers;

    HelperConfig public config;
    uint256 key;

    function setUp() public {
        // vm.createSelectFork(vm.envString("ETHEREUM_RPC_URL"));
        config = new HelperConfig();

        key = config.activeNetworkConfig();

        vm.startBroadcast(key);
        numbers = new ECPoints();
        vm.stopBroadcast();
    }

    function testHomework1() public {
        ECPoints.ECPoint memory A = ECPoints.ECPoint({
            x: 2857625431839718922471812833357737477490018756027287331750692909542658596388,
            y: 1911129795864509240059974873783816568594673160967429852131769465429209708149
        });

        ECPoints.ECPoint memory B = ECPoints.ECPoint({
            x: 6507360157155643158246437866216908737331325167192999439393120007011009391516,
            y: 11652714823384767328267007200940860978557908365702675300479140657484167362413
        });
        uint256 num = 19;
        uint256 den = 12;

        console.log(numbers.rationalAdd(A, B, num, den));
    }

    function testHomework2() public view {
        ECPoints.ECPoint memory A = ECPoints.ECPoint({
            x: 1368015179489954701390400359078579693043519447331113978918064868415326638035,
            y: 9918110051302171585080402603319702774565515993150576347155970296011118125764
        });

        ECPoints.ECPoint memory B = ECPoints.ECPoint({
            x: 10744596414106452074759370245733544594153395043370666422502510773307029471145,
            y: 848677436511517736191562425154572367705380862894644942948681172815252343932
        });

        // dimension
        uint256 n = 2;

        // matrix
        uint256[][] memory matrix = new uint256[][](n);
        uint256[] memory row1 = new uint256[](n);
        row1[0] = 2;
        row1[1] = 20;
        matrix[0] = row1;
        uint256[] memory row2 = new uint256[](n);
        row2[0] = 3;
        row2[1] = 4;
        matrix[1] = row2;

        // EC points vector
        ECPoints.ECPoint[] memory points = new ECPoints.ECPoint[](n);
        points[0] = A;
        points[1] = B;

        // result vector
        uint256[] memory o = new uint256[](n);
        o[0] = 104;
        o[1] = 26;

        console.log(numbers.matmul(matrix, n, points, o));
    }
}
