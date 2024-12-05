<template>
    <div className="content">
            <h1>Ako začať</h1>
            <p>
                Po prihlásení si môžete vytvárať vlastné testy, spravovať ich, a následne ich zdieľať prostredníctvom
                unikátnych odkazov alebo hesiel. Testy môžete prispôsobiť podľa svojich potrieb a cielene zamerať na
                špecifické oblasti. Výsledky testov si viete prehľadne prezerať a hodnotiť priamo v svojom profile,
                pričom všetky údaje sú bezpečne uložené.
            </p>
            <p>
                Po zadaní odkazu alebo hesla môžete vyplniť testy jednoducho a z pohodlia domova. Platforma vám zároveň
                umožňuje kedykoľvek sa vrátiť k nevyplneným testom alebo si prezrieť históriu dokončených testov, ak vám
                to bolo umožnené psychológom.
            </p>
        </div>
</template>

<script>
export default{
    name: 'ContentComp'
}
</script>
<style>
.content {
    max-width: 900px;
    margin: 0 auto;
    text-align: justify;
    padding: 20px;
    padding-bottom: 50px;
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
}

.content h1 {
    padding: 5px 20px;
    margin-top: 0;
    margin-bottom: 20px;
    font-size: var(--h1-size);
    font-weight: bold;
    color: var(--color-h1);
    position: relative;
}

.content h1::before {
    content: '';
    position: absolute;
    left: 0px;
    top: 0;
    width: 10px;
    height: 100%;
    background-color: #dcd3ff;
    border-radius: 5px;
}

.content p {
    font-size: 18px;
    color: #666;
    margin: 10px 0;
}
</style>