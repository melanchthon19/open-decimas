# open-decimas

Are machines able to write decimas? Let's find out.

<img src="https://user-images.githubusercontent.com/61199264/103969615-34d3bf00-515e-11eb-8a62-e6c0fb96e760.png" width="480">

In order to generate decimas, two main classes are used: **Silabeador** that counts metric syllables and **Payador** that generates a poem.

## Silabeador

Silabeador is the main class that counts metric syllables of a given sentence.

For each sentence, it converts the raw ortography to phonemes, then to its underlying structure, it separates each syllable according to the structure, and finally it adds a hyphen as a separator to the raw ortography. An example is shown below:

**Example: Violeta Parra - De tal palo, tal astilla**  

de tal palo, tal astilla --> de-tal-pa-lo-tal-as-ti-La [8]\
se dequivoca el refrán --> se-de-ki-bo-kael-re-frán [8]\
solo le cuadra a san juan --> so-lo-le-kua-draa-san-xuan [8]\
pero no a esta mocosilla --> pe-ro-noaes-ta-mo-ko-si-La [8]\
bien dorá’ fue la tortilla --> bien-do-rá-fue-la-tor-ti-La [8]\
muy revueltita después --> mui-re-buel-ti-ta-des-pués [8]\
ya ven, mi abuelo josé --> ia-ben-mia-bue-lo-xo-sé [8]\
con el código en su mente --> kon-el-kó-di-goen-su-men-te [8]\
y quién hubo más prudente --> i-kién-u-bo-más-pru-den-te [8]\
como mi otro abuelo fue --> ko-mo-mio-troa-bue-lo-fue [8]\
tan sabios conocimientos --> tan-sa-bios-ko-no-si-mien-tos [8]\
no recayeron en hijos --> no-re-ka-ie-ron-en-i-xos [8]\
con un misterio prolijo --> kon-un-mis-te-rio-pro-li-xo [8]\
pasan directo a los nietos --> pa-san-di-rek-toa-los-nie-tos [8]\
en lo cual yo no les miento --> en-lo-kual-io-no-les-mien-to [8]\
tengo la prueba en la mano --> ten-go-la-prue-baen-la-ma-no [8]\
yo les presento a mi hermano --> io-les-pre-sen-toa-mier-ma-no [8]\
como el más bonito ejemplo --> ko-moel-más-bo-ni-toe-xem-plo [8]\
si ahora no tiene un templo --> sia-o-ra-no-tie-neun-tem-plo [8]\
lo tendrá tarde o temprano --> lo-ten-drá-tar-deo-tem-pra-no [8]\
muy revueltita después --> mui-re-buel-ti-ta-des-pués [8]

When counting syllables, it applies sinalefa, the poetic license to merge two vowels from contigous words into one syllable. For example, `pre-sen-to-a-mi-er-ma-no` would be `pre-sen-toa-mier-ma-no`.

## Payador

Payador is the main class that generates a poem using BETO model. I will add further details of its implementation soon.

Examples of generated poems:

**1**  
la casa tuya más profunda habita dónde  
Sin razón ter es amor  
quiero dar pre de celos  
aquí nos enti enterrar ambos  
más las or vas haciendo  
cosas ti misma pasa toda  
Nada somos insen del espíritu  
sobre esos dichos tiempos era  
del hecho tru la posibilidad  
más hacer pues dos medidas  
mediante así proceder posteriormente sucesivamente  
dar entrada correspondiente sus órdenes  

**2**  
la casa trans si ni la hace  
Pues otra nos cantar cuando  
la en otras escuelas sé  
para este mismo hecho esto  
podrá contribuir su vida todo  
un dolor exten ti tú  
ir mano segura has prestado  
le debo si dije silencio  
vi Cuando tu ser conociste  
Mi lengua ya respi respirando  
hasta mirar af del nido  
Porque da tu beso delicioso  

**3**  
la casa sino nadie se niega aún  
por es van don tal  
Quien pide ro está perdida  
Como queriendo ref lle lo  
que sin chist ten otro  
El artículo puede consultar consentimiento  
entre como letra particular adecuada  
dos opciones geomé que bien  
podrían generar multiplic trabajo resulta  
así módulos ex plantas paralelas  
que inter tre ella también  
cuando la mas lejos volvía  


## TODO
**Silabeador:**
- further preprocessing for non-alphabetic characters
- non-spanish words
- sinéresis
- diéresis
- rhyme
**Payador:**
- try different techniques for generating a poem
- constraint number of syllables using Silabeador

## Credits
Image from: https://www.patrimoniocultural.gob.cl/614/w3-article-5398.html?_noredirect=1  
BETO model from: https://github.com/dccuchile/beto
