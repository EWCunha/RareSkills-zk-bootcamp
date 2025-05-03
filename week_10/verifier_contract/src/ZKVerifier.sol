// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.25;

contract ZKVerifier {
    struct G1Point {
        uint256 x;
        uint256 y;
    }

    struct G2Point {
        uint256 x1;
        uint256 x2;
        uint256 y1;
        uint256 y2;
    }

    address public constant ADD_POINTS = address(6);
    address public constant MUL_SCALAR = address(7);
    address public constant PAIRING = address(8);

    uint256 constant FIELD_MODULUS =
        21888242871839275222246405745257275088696311157297823662689037894645226208583;
    uint256 constant CURVE_ORDER =
        21888242871839275222246405745257275088548364400416034343698204186575808495617;

    G1Point public alpha1 =
        G1Point({
            x: 3927092674152154001037919440146790233361956899612023537741659305499385084031,
            y: 15514573173146200595016466135822141999394505178480103495696271267158458098108
        });

    G2Point public beta2 =
        G2Point({
            x1: 710971659950299075351025638299543031158944726718316196630017563250057256894,
            x2: 21096988598549379316064222604087070093107208963851932395621890487284397317911,
            y1: 19625443649200586548833881985732606703875589975722291103262484117838349784384,
            y2: 18248024739783836328211815967314311276769976803340453674090473449195891572055
        });

    G2Point public delta2 =
        G2Point({
            x1: 15512671280233143720612069991584289591749188907863576513414377951116606878472,
            x2: 18551411094430470096460536606940536822990217226529861227533666875800903099477,
            y1: 13376798835316611669264291046140500151806347092962367781523498857425536295743,
            y2: 1711576522631428957817575436337311654689480489843856945284031697403898093784
        });

    G2Point public gamma2 =
        G2Point({
            x1: 16137324789686743234629608741537369181251990815455155257427276976918350071287,
            x2: 280672898440571232725436467950720547829638241593507531241322547969961007057,
            y1: 12136420650226457477690750437223209427924916790606163705631661913973995426040,
            y2: 17641806683785498955878869918183868440783188556637975525088932771694068429840
        });

    function getPubPoints() internal pure returns (G1Point[3] memory) {
        G1Point[3] memory pub = [
            G1Point({
                x: 10337475377762410320521579863105796871218321230420005046205878746972625295731,
                y: 1495048457365898187519834633700919271787955170421098986403402119132116191726
            }),
            G1Point({
                x: 10712153340532120499948892745447231641614624829424121384410621714449025520578,
                y: 13005741037594483073753867627097971194091137955625648821701624553791110875530
            }),
            G1Point({
                x: 21390865706894450335960544517685327293709734921651646903544711473699990159653,
                y: 8730056461702139016056874249139930033793812075116629602778941190532755168610
            })
        ];

        return pub;
    }

    function neg(G1Point memory point) internal pure returns (G1Point memory) {
        if (point.x == 0 && point.y == 0) {
            return G1Point(0, 0);
        }

        return
            G1Point({x: point.x, y: FIELD_MODULUS - (point.y % FIELD_MODULUS)});
    }

    function add(
        G1Point memory point1,
        G1Point memory point2
    ) internal view returns (G1Point memory) {
        (bool ok, bytes memory returnedValue) = ADD_POINTS.staticcall(
            abi.encode(point1.x, point1.y, point2.x, point2.y)
        );

        require(ok, "Add failed");
        (uint256 x, uint256 y) = abi.decode(returnedValue, (uint256, uint256));

        return G1Point({x: x, y: y});
    }

    function mul(
        G1Point memory point,
        uint256 scalar
    ) internal view returns (G1Point memory) {
        (bool ok, bytes memory returnedValue) = MUL_SCALAR.staticcall(
            abi.encode(point.x, point.y, scalar)
        );

        require(ok, "Mul failed");
        (uint256 x, uint256 y) = abi.decode(returnedValue, (uint256, uint256));

        return G1Point({x: x, y: y});
    }

    function pairing(
        G1Point memory a1,
        G2Point memory b2,
        G1Point memory c1,
        G1Point memory pub1
    ) public view returns (bool) {
        G1Point[4] memory p1 = [neg(a1), alpha1, pub1, c1];
        G2Point[4] memory p2 = [b2, beta2, gamma2, delta2];

        uint256 inputSize = 24;
        uint256[] memory input = new uint256[](inputSize);

        for (uint256 i = 0; i < 4; i++) {
            uint256 j = i * 6;
            input[j + 0] = p1[i].x;
            input[j + 1] = p1[i].y;
            input[j + 2] = p2[i].x2;
            input[j + 3] = p2[i].x1;
            input[j + 4] = p2[i].y2;
            input[j + 5] = p2[i].y1;
        }

        (bool success, bytes memory returned) = PAIRING.staticcall(
            abi.encodePacked(input)
        );
        require(success, "pairing failed");

        return abi.decode(returned, (bool));
    }

    function verify(
        uint256[3] memory pubInputs,
        G1Point memory A1,
        G2Point memory B2,
        G1Point memory C1
    ) external view returns (bool) {
        G1Point memory vk = G1Point({x: 0, y: 0});
        G1Point[3] memory pub = getPubPoints();

        for (uint8 i = 0; i < 3; ++i) {
            require(pubInputs[i] < CURVE_ORDER, "invalid inputs");
            vk = add(vk, mul(pub[i], pubInputs[i]));
        }

        return pairing(A1, B2, C1, vk);
    }
}
